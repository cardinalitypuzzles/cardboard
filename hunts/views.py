import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.base import RedirectView
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import assign_perm, get_objects_for_user

from google_api_lib.tasks import sync_drive_permissions_for_hunt
from puzzles.models import PuzzleTag

from .forms import HuntForm, HuntSettingsForm
from .models import Hunt

logger = logging.getLogger(__name__)


@login_required(login_url="/")
def index(request):
    form = HuntForm()

    if request.method == "POST":
        if request.user.is_staff:
            form = HuntForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    hunt = Hunt(
                        name=form.cleaned_data["name"],
                        url=form.cleaned_data["url"],
                        start_time=form.cleaned_data["start_time"],
                        end_time=form.cleaned_data["end_time"],
                    )
                    hunt.save()

                    assign_perm("hunt_admin", request.user, hunt)
                    assign_perm("hunt_access", request.user, hunt)

                    if form.cleaned_data["populate_tags"]:
                        transaction.on_commit(
                            lambda: PuzzleTag.create_default_tags(hunt)
                        )

                return redirect(reverse("hunts:edit", kwargs={"hunt_slug": hunt.slug}))
        else:
            return HttpResponseForbidden()

    context = {
        "active_hunts": get_objects_for_user(request.user, "hunt_access", klass=Hunt)
        .filter(active=True)
        .order_by("-created_on"),
        "finished_hunts": get_objects_for_user(request.user, "hunt_access", klass=Hunt)
        .filter(active=False)
        .order_by("-created_on"),
        "form": form,
    }
    return render(request, "index.html", context)


@login_required(login_url="/")
@permission_required_or_403("hunt_admin", (Hunt, "slug", "hunt_slug"))
def edit(request, hunt_slug):
    if request.method == "POST":
        with transaction.atomic():
            hunt = get_object_or_404(Hunt.objects.select_for_update(), slug=hunt_slug)
            hunt_form = HuntForm(request.POST, instance=hunt)
            settings_form = HuntSettingsForm(request.POST, instance=hunt.settings)
            if hunt_form.is_valid() and settings_form.is_valid():
                hunt_form.save()
                settings_form.save()

                if hunt_form.cleaned_data["populate_tags"]:
                    transaction.on_commit(lambda: PuzzleTag.create_default_tags(hunt))
                else:
                    transaction.on_commit(lambda: PuzzleTag.remove_default_tags(hunt))

                messages.success(request, "Hunt settings saved.")
                return redirect(reverse("hunts:edit", kwargs={"hunt_slug": hunt.slug}))

    else:
        hunt = Hunt.get_object_or_404(user=request.user, slug=hunt_slug)
        hunt_form = HuntForm(instance=hunt)
        settings_form = HuntSettingsForm(instance=hunt.settings)

    context = {
        "hunt": hunt,
        "hunt_form": hunt_form,
        "settings_form": settings_form,
    }
    return render(request, "edit.html", context)


@login_required(login_url="/")
@permission_required_or_403("hunt_access", (Hunt, "slug", "hunt_slug"))
def redirect_to_drive(request, hunt_slug):
    hunt = get_object_or_404(Hunt.objects.select_related("settings"), slug=hunt_slug)
    human_url = hunt.settings.google_drive_human_url
    if human_url:
        return HttpResponseRedirect(human_url)
    else:
        messages.error(
            request,
            f"Cannot redirect to Google folder. Did you set a human Drive URL setting?",
        )
        return redirect("/")


def _queue_discord_role_sync(hunt_slug):
    import chat.tasks

    chat.tasks.sync_roles.delay(
        hunt_slug,
        settings.CHAT_DEFAULT_SERVICE,
    )


def _queue_drive_permission_sync(request, hunt_slug):
    hunt = Hunt.get_object_or_404(user=request.user, slug=hunt_slug)
    sync_drive_permissions_for_hunt.delay(hunt.id)


@login_required(login_url="/")
@permission_required_or_403("hunt_admin", (Hunt, "slug", "hunt_slug"))
def sync(request, hunt_slug):
    if request.method != "POST":
        return HttpResponseForbidden()

    _queue_discord_role_sync(hunt_slug)
    _queue_drive_permission_sync(request, hunt_slug)

    messages.success(request, "Discord roles synced and users added to hunt.")
    return redirect(reverse("hunts:edit", kwargs={"hunt_slug": hunt_slug}))


@login_required(login_url="/")
@permission_required_or_403("hunt_admin", (Hunt, "slug", "hunt_slug"))
def sync_discord_roles(request, hunt_slug):
    if request.method != "POST":
        return HttpResponseForbidden()

    _queue_discord_role_sync(hunt_slug)

    messages.success(request, "Discord roles created.")
    return redirect(f"/hunts/{hunt_slug}/edit")


@permission_required_or_403("hunt_admin", (Hunt, "slug", "hunt_slug"))
def sync_drive_permissions(request, hunt_slug):
    if request.method != "POST":
        return HttpResponseForbidden()

    _queue_drive_permission_sync(request, hunt_slug)

    messages.success(request, "Users added to hunt")
    return redirect(f"/hunts/{hunt_slug}/edit")


class LastAccessedHuntRedirectView(LoginRequiredMixin, RedirectView):
    login_url = "/"
    pattern_name = "hunts:all_puzzles_react"

    def get_redirect_url(self, *args, **kwargs):
        hunt = self.request.user.last_accessed_hunt
        if not hunt or not hunt.active:
            return reverse("hunts:index")
        kwargs["hunt_slug"] = hunt.slug
        return super().get_redirect_url(*args, **kwargs)


class ReactHuntView(LoginRequiredMixin, View):
    login_url = "/"
    redirect_field_name = "next"

    def get(self, request, hunt_slug):
        hunt = Hunt.get_object_or_404(user=request.user, slug=hunt_slug)
        if not request.user.has_perm("hunt_access", hunt):
            raise PermissionDenied()

        context = {
            "hunt_pk": hunt.pk,
        }
        return render(request, "all_puzzles_react.html", context)

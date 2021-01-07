from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.base import RedirectView

from .forms import HuntForm
from .models import Hunt

import logging


logger = logging.getLogger(__name__)


@login_required(login_url="/")
def index(request):
    form = HuntForm()

    if request.method == "POST":
        form = HuntForm(request.POST)
        if form.is_valid():
            hunt = Hunt(name=form.cleaned_data["name"], url=form.cleaned_data["url"])
            hunt.save()

    context = {
        "active_hunts": Hunt.objects.filter(active=True).order_by("-created_on"),
        "finished_hunts": Hunt.objects.filter(active=False).order_by("-created_on"),
        "form": form,
    }
    return render(request, "index.html", context)


class LastAccessedHuntRedirectView(LoginRequiredMixin, RedirectView):
    login_url = "/"
    pattern_name = "hunts:all_puzzles_react"

    def get_redirect_url(self, *args, **kwargs):
        hunt = self.request.user.last_accessed_hunt
        if not hunt:
            return reverse("hunts:index")
        kwargs["hunt_slug"] = hunt.slug
        return super().get_redirect_url(*args, **kwargs)


class ReactHuntView(LoginRequiredMixin, View):
    login_url = "/"
    redirect_field_name = "next"

    def get(self, request, hunt_slug):
        hunt = Hunt.get_object_or_404(user=request.user, slug=hunt_slug)

        context = {
            "hunt_pk": hunt.pk,
        }
        return render(request, "all_puzzles_react.html", context)

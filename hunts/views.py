from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic.base import RedirectView

from url_normalize import url_normalize

from .forms import HuntForm
from .models import Hunt
from google_api_lib.google_api_client import GoogleApiClient
from puzzles.forms import PuzzleForm
from puzzles.models import Puzzle
from puzzles.puzzle_tree import PuzzleTree

import logging


logger = logging.getLogger(__name__)


@login_required(login_url="/accounts/login/")
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


def __table_status_class(puzzle):
    if puzzle.status == Puzzle.PENDING:
        return "table-warning"
    elif puzzle.status == Puzzle.EXTRACTION:
        return "table-danger"
    elif puzzle.status == Puzzle.SOLVED:
        return "table-success"
    elif puzzle.status == Puzzle.STUCK:
        return "table-danger"
    else:
        return ""


def __get_puzzle_class(sorted_np_pairs):
    puzzle_class = [__table_status_class(pair.node.puzzle) for pair in sorted_np_pairs]
    most_recent_treegrid_id = {}
    for i, pair in enumerate(sorted_np_pairs):
        node = pair.node
        parent = pair.parent
        treegrid_id = i + 1
        most_recent_treegrid_id[node.puzzle.pk] = treegrid_id
        puzzle_class[i] += " treegrid-%i" % treegrid_id
        if parent and parent.puzzle != None:
            # Most recently seen treegrid_id for parent
            parent_treegrid_id = most_recent_treegrid_id.get(parent.puzzle.pk, 0)
            if parent_treegrid_id > 0:
                puzzle_class[i] += " treegrid-parent-%i" % parent_treegrid_id
        # If meta is solved, collapse the subtree.
        if len(node.children) > 0 and node.puzzle.is_solved():
            puzzle_class[i] += " initial-collapsed"
    return puzzle_class


@require_GET
@login_required(login_url="/accounts/login/")
def puzzles(request, slug):
    hunt = Hunt.get_object_or_404(user=request.user, slug=slug)
    puzzle_objects = (
        hunt.puzzles.all()
        .prefetch_related("metas")
        .prefetch_related("active_users")
        .prefetch_related("tags")
    )

    sorted_np_pairs = PuzzleTree(puzzle_objects).get_sorted_node_parent_pairs()
    sorted_puzzles = [pair.node.puzzle for pair in sorted_np_pairs]
    puzzle_classes = __get_puzzle_class(sorted_np_pairs)

    rows = zip(sorted_puzzles, puzzle_classes)

    result = {
        "data": [
            [
                puzzle.pk,
                puzzle.name,
                puzzle.url,
                puzzle.is_meta,
                [
                    "%s %s" % (user.first_name, user.last_name)
                    for user in puzzle.active_users.all()
                ],
                puzzle.answer,
                puzzle.status,
                puzzle.sheet,
                [[tag.name, tag.color] for tag in puzzle.tags.all()],
                "",
                puzzle_class,
            ]
            for puzzle, puzzle_class in rows
        ]
    }

    return JsonResponse(result)


class HuntView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    redirect_field_name = "next"

    def get(self, request, slug):
        if not Hunt.objects.filter(slug=slug).exists():
            return index(request)

        hunt = Hunt.get_object_or_404(user=request.user, slug=slug)
        form = PuzzleForm(auto_id=False)
        context = {
            "hunt_name": hunt.name,
            "hunt_slug": slug,
            "form": form,
        }

        return render(request, "all_puzzles.html", context)

    def __handle_dup_puzzle(self):
        message = "A puzzle with the given name already exists!"
        return JsonResponse({"error": message}, status=400)

    def post(self, request, slug):
        hunt = Hunt.get_object_or_404(user=request.user, slug=slug)
        form = PuzzleForm(request.POST)

        puzzle = None
        if form.is_valid():
            name = form.cleaned_data["name"]
            name = Puzzle.maybe_truncate_name(name)
            puzzle_url = url_normalize(form.cleaned_data["url"])
            is_meta = form.cleaned_data["is_meta"]

            # Early termination -- if a puzzle with given name exists, don't try to create
            # a new sheet. This is purely an optimization to avoid dangling
            # google sheets.
            already_exists = Puzzle.objects.filter(name=name).exists()
            already_exists = Puzzle.objects.filter(name=name, hunt=hunt).exists()
            if already_exists:
                return self.__handle_dup_puzzle()

            # TODO(erwa): Add error handling and refactor into google API lib.
            google_api_client = GoogleApiClient.getInstance()
            if google_api_client:
                sheet = google_api_client.create_google_sheets(name)
            else:
                logger.warn("Sheet not created for puzzle %s" % name)
                sheet = None

            if google_api_client:
                google_api_client.add_puzzle_link_to_sheet(puzzle_url, sheet)

            try:
                puzzle = Puzzle.objects.create(
                    name=name, url=puzzle_url, hunt=hunt, sheet=sheet, is_meta=is_meta
                )

            except IntegrityError as e:
                # TODO(asdfryan): Think about cleaning up dangling sheets.
                # TODO(asdfryan): Think about other catchable errors.
                return self.__handle_dup_puzzle()
        else:
            return JsonResponse(
                {
                    "error": "Puzzle not created because the form "
                    "was invalid. "
                    "Make sure the URL is actually a URL."
                },
                status=400,
            )

        result = [
            puzzle.pk,
            puzzle.name,
            puzzle.url,
            puzzle.is_meta,
            [
                "%s %s" % (user.first_name, user.last_name)
                for user in puzzle.active_users.all()
            ],
            puzzle.answer,
            puzzle.status,
            puzzle.sheet,
            [[tag.name, tag.color] for tag in puzzle.tags.all()],
            "",
            "treegrid-0 even",
        ]
        return JsonResponse({"data": result})


class LastAccessedHuntRedirectView(LoginRequiredMixin, RedirectView):
    login_url = "/accounts/login/"
    pattern_name = "hunts:all_puzzles"

    def get_redirect_url(self, *args, **kwargs):
        hunt = self.request.user.last_accessed_hunt
        if not hunt:
            return reverse("hunts:index")

        # Answer urls use pattern_name="answers:hunt_queue" and "hunt_slug" to
        # disambiguate between answer and hunt primary keys.
        if self.pattern_name == LastAccessedHuntRedirectView.pattern_name:
            kwargs["slug"] = hunt.slug
        else:
            kwargs["hunt_slug"] = hunt.slug
        return super().get_redirect_url(*args, **kwargs)


if settings.DEBUG:
    HuntView = method_decorator(csrf_exempt, name="dispatch")(HuntView)

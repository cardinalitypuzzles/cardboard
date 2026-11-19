import logging

from rest_framework import permissions

from hunts.models import Hunt

logger = logging.getLogger(__name__)


class HuntAccessPermission(permissions.BasePermission):
    message = "You do not have access to this hunt"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm("hunt_access", obj)
        else:
            return request.user.has_perm("hunt_admin", obj)


class PuzzleAccessPermission(permissions.BasePermission):
    message = "You do not have access to this puzzle"

    def has_permission(self, request, view):
        try:
            hunt = Hunt.objects.get(id=view.kwargs["hunt_id"])
        except Hunt.DoesNotExist:
            hunt = None

        if not hunt:
            return False

        return request.user.has_perm("hunt_access", hunt)

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("hunt_access", obj.hunt)


class HuntAccessViaPuzzleIdPermission(permissions.BasePermission):
    """Checks hunt_access on the hunt owning the view's "puzzle_id" kwarg.

    Routes nested under /puzzles/<puzzle_id>/ have no hunt_id to check, so the
    hunt is reached through the puzzle instead.
    """

    def has_permission(self, request, view):
        try:
            hunt = Hunt.objects.get(puzzles=view.kwargs["puzzle_id"])
        except Hunt.DoesNotExist:
            hunt = None

        if not hunt:
            return False

        return request.user.has_perm("hunt_access", hunt)


class PuzzleTagAccessPermission(HuntAccessViaPuzzleIdPermission):
    message = "You do not have access to this puzzle tag"

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("hunt_access", obj.hunt)


class AnswerAccessPermission(HuntAccessViaPuzzleIdPermission):
    message = "You do not have access to this answer"

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("hunt_access", obj.puzzle.hunt)


class PuzzleNotesAccessPermission(HuntAccessViaPuzzleIdPermission):
    message = "You do not have access to this puzzle"

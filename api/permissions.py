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
        logger.info("Just checkin some object permissions")
        return request.user.has_perm("hunt_access", obj.hunt)


class PuzzleTagAccessPermission(permissions.BasePermission):
    message = "You do not have access to this puzzle tag"

    def has_permission(self, request, view):
        try:
            hunt = Hunt.objects.get(puzzles=view.kwargs["puzzle_id"])
        except Hunt.DoesNotExist:
            hunt = None

        if not hunt:
            return False

        return request.user.has_perm("hunt_access", hunt)

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("hunt_access", obj.hunt)


class AnswerAccessPermission(permissions.BasePermission):
    message = "You do not have access to this answer"

    def has_permission(self, request, view):
        try:
            hunt = Hunt.objects.get(puzzles=view.kwargs["puzzle_id"])
        except Hunt.DoesNotExist:
            hunt = None

        if not hunt:
            return False

        logger.info("testing some answer obj perms")
        return request.user.has_perm("hunt_access", hunt)

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("hunt_access", obj.puzzle.hunt)

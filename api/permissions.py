import logging

from rest_framework import permissions

from hunts.models import Hunt

logger = logging.getLogger(__name__)


class HuntAccessPermission(permissions.BasePermission):
    """Requires a permission on the hunt the request concerns.

    The hunt comes from whichever kwarg the route carries, and from the object
    itself on detail routes -- every hunt-scoped model answers get_hunt().
    """

    message = "You do not have access to this hunt"
    read_perm = "hunt_access"
    write_perm = "hunt_access"

    def _required_perm(self, request):
        if request.method in permissions.SAFE_METHODS:
            return self.read_perm
        return self.write_perm

    def has_permission(self, request, view):
        if "hunt_id" in view.kwargs:
            hunt = Hunt.objects.filter(pk=view.kwargs["hunt_id"]).first()
        elif "puzzle_id" in view.kwargs:
            hunt = Hunt.objects.filter(puzzles=view.kwargs["puzzle_id"]).first()
        else:
            # A hunt's own routes identify it by pk, so there is nothing to
            # check until get_object() calls has_object_permission below.
            return True

        if not hunt:
            return False

        return request.user.has_perm(self._required_perm(request), hunt)

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm(self._required_perm(request), obj.get_hunt())


class HuntAdminPermission(HuntAccessPermission):
    """Reading a hunt needs access; changing one needs admin."""

    write_perm = "hunt_admin"

"""Authorization matrix for every API route.

Asserts which callers each route refuses, independent of what the route then
does. This exists so that changes to the permission classes have to prove they
did not move a cell: the only interesting value is 403 vs not-403.
"""

from django.test import override_settings
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from accounts.models import Puzzler
from answers.models import Answer
from api.permissions import HuntAdminPermission
from hunts.models import Hunt
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag

ANONYMOUS = "anonymous"
NO_PERMS = "authenticated, no hunt perms"
ACCESS = "hunt_access"
ADMIN = "hunt_access + hunt_admin"

# Every route requires hunt_access. Writes to a hunt itself require hunt_admin,
# but no unsafe method is routed to HuntViewSet, so no cell exercises that yet.
EXPECTED_DENIED = {ANONYMOUS: True, NO_PERMS: True, ACCESS: False, ADMIN: False}


@override_settings(
    CHAT_DEFAULT_SERVICE=None,
    CHAT_SERVICES={},
    GOOGLE_API_AUTHN_INFO=None,
)
class PermissionMatrixTests(APITestCase):
    def _client_for(self, level):
        client = APIClient()
        if level == ANONYMOUS:
            return client
        user = Puzzler.objects.create_user(
            username=f"u-{level}",
            email=f"{level}@t.com".replace(" ", ""),
            password="pw",
        )
        if level in (ACCESS, ADMIN):
            assign_perm("hunt_access", user, self.hunt)
        if level == ADMIN:
            assign_perm("hunt_admin", user, self.hunt)
        client.force_login(user)
        return client

    def setUp(self):
        self.hunt = Hunt.objects.create(name="matrix hunt", url="m.com")

    def _fixtures(self, tag):
        """Objects for one probe run, created through the ORM so that the
        matrix measures the routes rather than its own setup."""
        puzzle = Puzzle.objects.create(
            name=f"pz-{tag}", hunt=self.hunt, url=f"{tag}.com", sheet=f"s-{tag}"
        )
        doomed = Puzzle.objects.create(
            name=f"doomed-{tag}", hunt=self.hunt, url=f"d{tag}.com", sheet=f"d-{tag}"
        )
        answer = Answer.objects.create(text=f"ANS{tag}", puzzle=puzzle)
        doomed_answer = Answer.objects.create(text=f"DOOM{tag}", puzzle=puzzle)
        puzzle_tag = PuzzleTag.objects.create(name=f"tag-{tag}", hunt=self.hunt)
        puzzle.tags.add(puzzle_tag)
        return puzzle, doomed, answer, doomed_answer, puzzle_tag

    def _probe(self, level, slug):
        client = self._client_for(level)
        pz, doomed, ans, doomed_ans, tag = self._fixtures(slug)
        h, p = self.hunt.pk, pz.pk
        payload = {"name": f"new-{slug}", "url": f"n{slug}.com", "is_meta": False}

        return [
            ("GET    /hunts/{id}", client.get(f"/api/v1/hunts/{h}")),
            ("GET    /hunts/{id}/puzzles", client.get(f"/api/v1/hunts/{h}/puzzles")),
            (
                "POST   /hunts/{id}/puzzles",
                client.post(f"/api/v1/hunts/{h}/puzzles", payload),
            ),
            (
                "GET    /hunts/{id}/puzzles/{id}",
                client.get(f"/api/v1/hunts/{h}/puzzles/{p}"),
            ),
            (
                "PATCH  /hunts/{id}/puzzles/{id}",
                client.patch(f"/api/v1/hunts/{h}/puzzles/{p}", {"notes": "x"}),
            ),
            (
                "DELETE /hunts/{id}/puzzles/{id}",
                client.delete(f"/api/v1/hunts/{h}/puzzles/{doomed.pk}"),
            ),
            (
                "POST   /puzzles/{id}/answers",
                client.post(f"/api/v1/puzzles/{p}/answers", {"text": f"X{slug}"}),
            ),
            (
                "PATCH  /puzzles/{id}/answers/{id}",
                client.patch(
                    f"/api/v1/puzzles/{p}/answers/{ans.pk}", {"text": f"Y{slug}"}
                ),
            ),
            (
                "DELETE /puzzles/{id}/answers/{id}",
                client.delete(f"/api/v1/puzzles/{p}/answers/{doomed_ans.pk}"),
            ),
            (
                "POST   /puzzles/{id}/tags",
                client.post(
                    f"/api/v1/puzzles/{p}/tags",
                    {"name": f"t{slug}", "color": "primary"},
                ),
            ),
            (
                "GET    /puzzles/{id}/tags/{id}",
                client.get(f"/api/v1/puzzles/{p}/tags/{tag.pk}"),
            ),
            (
                "DELETE /puzzles/{id}/tags/{id}",
                client.delete(f"/api/v1/puzzles/{p}/tags/{tag.pk}"),
            ),
            (
                "POST   /puzzles/{id}/notes",
                client.post(f"/api/v1/puzzles/{p}/notes", {"text": "n"}),
            ),
        ]

    def _assert_level(self, level, slug):
        expected = EXPECTED_DENIED[level]
        rows = self._probe(level, slug)
        print(f"\n  {level}")
        for label, response in rows:
            denied = response.status_code == status.HTTP_403_FORBIDDEN
            mark = "DENIED " if denied else "allowed"
            print(f"    {mark}  {label}  [{response.status_code}]")
            self.assertEqual(
                denied,
                expected,
                f"{level} on {label}: got {response.status_code}, "
                f"expected {'403' if expected else 'not 403'}",
            )

    def test_anonymous(self):
        self._assert_level(ANONYMOUS, "anon")

    def test_authenticated_without_hunt_permissions(self):
        self._assert_level(NO_PERMS, "noperm")

    def test_hunt_access(self):
        self._assert_level(ACCESS, "access")

    def test_hunt_admin(self):
        self._assert_level(ADMIN, "admin")

    def test_hunt_writes_require_admin(self):
        """No route exposes a hunt write yet, so the matrix above cannot cover
        this. Asserted directly so that adding such a route inherits the
        policy rather than quietly widening it."""
        factory = APIRequestFactory()
        permission = HuntAdminPermission()

        member = Puzzler.objects.create_user(
            username="member", email="m@t.com", password="pw"
        )
        assign_perm("hunt_access", member, self.hunt)
        admin = Puzzler.objects.create_user(
            username="admin", email="a@t.com", password="pw"
        )
        assign_perm("hunt_access", admin, self.hunt)
        assign_perm("hunt_admin", admin, self.hunt)

        cases = [
            ("read", factory.get("/"), member, True),
            ("read", factory.get("/"), admin, True),
            ("write", factory.patch("/"), member, False),
            ("write", factory.patch("/"), admin, True),
        ]
        for kind, request, user, expected in cases:
            request.user = user
            allowed = permission.has_object_permission(request, None, self.hunt)
            self.assertEqual(
                allowed,
                expected,
                f"{user.username} {kind} on hunt: expected "
                f"{'allowed' if expected else 'denied'}",
            )

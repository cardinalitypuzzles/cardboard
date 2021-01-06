from rest_framework.test import APITestCase
from accounts.models import Puzzler
from hunts.models import Hunt
from puzzles.models import PuzzleTag


class SmallboardTestCase(APITestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self.client.login(username="test", password="testingpwd")

        self._hunt = Hunt.objects.create(name="fake hunt", url="google.com")

    def tearDown(self):
        for tag in PuzzleTag.objects.all():
            tag.delete()

        self._hunt.delete()

    # Hunt methods

    def get_hunt(self):
        return self.client.get(f"/api/v1/hunts/{self._hunt.pk}")

    # Puzzle methods

    def create_puzzle(self, data):
        return self.client.post(f"/api/v1/hunts/{self._hunt.pk}/puzzles", data)

    def delete_puzzle(self, pk):
        return self.client.delete(f"/api/v1/hunts/{self._hunt.pk}/puzzles/{pk}")

    def edit_puzzle(self, pk, data):
        return self.client.patch(f"/api/v1/hunts/{self._hunt.pk}/puzzles/{pk}", data)

    def list_puzzles(self):
        return self.client.get(f"/api/v1/hunts/{self._hunt.pk}/puzzles")

    # Tag methods

    def create_tag(self, puzzle_id, data):
        return self.client.post(
            f"/api/v1/hunts/{self._hunt.pk}/puzzles/{puzzle_id}/tags", data
        )

    def delete_tag(self, puzzle_id, pk):
        return self.client.delete(
            f"/api/v1/hunts/{self._hunt.pk}/puzzles/{puzzle_id}/tags/{pk}"
        )

    # Answer methods

    def create_answer(self, puzzle_id, data):
        return self.client.post(
            f"/api/v1/hunts/{self._hunt.pk}/puzzles/{puzzle_id}/answers", data
        )

    def delete_answer(self, puzzle_id, pk):
        return self.client.delete(
            f"/api/v1/hunts/{self._hunt.pk}/puzzles/{puzzle_id}/answers/{pk}"
        )

    def edit_answer(self, puzzle_id, pk, data):
        return self.client.patch(
            f"/api/v1/hunts/{self._hunt.pk}/puzzles/{puzzle_id}/answers/{pk}", data
        )

from django.test import TestCase
from guardian.shortcuts import assign_perm

from accounts.models import Puzzler
from cardboard import views
from hunts.models import Hunt


class TestHomePage(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )

        self._test_hunt = Hunt.objects.create(name="hunt1", url="hunt1.com")
        assign_perm("hunt_admin", self._user, self._test_hunt)
        assign_perm("hunt_access", self._user, self._test_hunt)

    def tearDown(self):
        self._test_hunt.delete()
        self._user.delete()

    def testLoggedOutHomePage(self):
        response = self.client.get("/")
        self.assertEqual(response.resolver_match.func, views.home)
        self.assertTemplateUsed(response, "home.html")

    def testLoggedInHomePages(self):
        self.client.login(username="test", password="testingpwd")
        response = self.client.get("/")
        self.assertRedirects(response, "/hunts/")

        Puzzler.objects.filter(pk=self._user.pk).update(
            last_accessed_hunt=self._test_hunt
        )
        response = self.client.get("/")
        self.assertRedirects(response, "/hunts/hunt1/")

    def testLoggedOutToolsPage(self):
        response = self.client.get("/tools")
        self.assertRedirects(response, "/?next=/tools")

    def testLoggedInToolsPage(self):
        self.client.login(username="test", password="testingpwd")
        response = self.client.get("/tools")
        self.assertTemplateUsed(response, "tools.html")

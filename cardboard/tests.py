from django.test import TestCase
from django.urls import reverse
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


class TestLogout(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )

    def tearDown(self):
        self._user.delete()

    def testLogoutRejectsGet(self):
        # Django 5.0 dropped GET support from LogoutView; a GET must not log
        # the user out, and must not 500.
        self.client.login(username="test", password="testingpwd")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def testLogoutAcceptsPost(self):
        self.client.login(username="test", password="testingpwd")
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def testNavLogoutIsAPostForm(self):
        # Guards against the nav reverting to a plain <a href>, which renders
        # a 405 page on every click.
        self.client.login(username="test", password="testingpwd")
        response = self.client.get("/tools")
        self.assertContains(response, 'action="%s"' % reverse("logout"))
        self.assertNotContains(response, 'href="%s"' % reverse("logout"))


class TestTaskPriority(TestCase):
    def testHighPriorityIsConsumedFirstOnRedis(self):
        # kombu's Redis transport stores each priority in its own list and
        # polls them in priority_steps order, so the bucket a priority maps to
        # determines consumption order. Guards against the enum being flipped
        # back to RabbitMQ semantics (higher number = more urgent).
        from kombu.transport.redis import Channel

        from cardboard.settings import TaskPriority

        steps = list(Channel.priority_steps)

        def poll_position(priority):
            return steps.index(Channel.priority(Channel, priority.value))

        self.assertLess(
            poll_position(TaskPriority.HIGH), poll_position(TaskPriority.MED)
        )
        self.assertLess(
            poll_position(TaskPriority.MED), poll_position(TaskPriority.LOW)
        )

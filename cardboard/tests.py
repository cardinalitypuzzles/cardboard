import os
import tempfile
from unittest import mock

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm

from accounts.models import Puzzler
from cardboard import env, views
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


class TestLoadEnv(SimpleTestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        for patcher in (
            mock.patch.object(env, "BASE_DIR", self.dir),
            mock.patch.object(env, "_loaded", False),
            mock.patch.dict(os.environ, clear=True),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def write(self, name, contents):
        with open(os.path.join(self.dir, name), "w") as f:
            f.write(contents)

    def load(self, argv):
        with mock.patch("sys.argv", argv):
            env.load_env()

    def testTestRunNeverLoadsDotEnv(self):
        self.write(".env", "SECRET_TOKEN=live\nONLY_IN_ENV=live\n")
        self.write(".env.test", "SECRET_TOKEN=test\n")
        self.load(["manage.py", "test"])
        self.assertEqual(os.environ.get("SECRET_TOKEN"), "test")
        self.assertNotIn("ONLY_IN_ENV", os.environ)

    def testTestRunPrefersUserTestFile(self):
        self.write(".env.test.user", "WHICH=user\n")
        self.write(".env.test", "WHICH=shared\nONLY_IN_SHARED=1\n")
        self.load(["manage.py", "test"])
        self.assertEqual(os.environ.get("WHICH"), "user")
        self.assertNotIn("ONLY_IN_SHARED", os.environ)

    def testNonTestRunLoadsDotEnv(self):
        self.write(".env", "WHICH=env\n")
        self.write(".env.test", "WHICH=test\n")
        self.load(["manage.py", "runserver"])
        self.assertEqual(os.environ.get("WHICH"), "env")

    def testLaterCallsAreNoOps(self):
        # Regression: cardboard.celery used to load .env unconditionally after
        # manage.py had loaded .env.test, filling in the live credentials.
        self.write(".env", "SECRET_TOKEN=live\n")
        self.write(".env.test", "OTHER=test\n")
        self.load(["manage.py", "test"])
        self.load(["celery", "-A", "cardboard", "worker"])
        self.assertNotIn("SECRET_TOKEN", os.environ)

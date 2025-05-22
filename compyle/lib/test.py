# pylint: disable=invalid-name

from datetime import datetime

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory, APITestCase

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case class to be extended by `BaseApiTest` and `BaseAdminTest`."""

    maxDiff = None

    def setUp(self) -> None:
        """Set up the test environment with user and anonymous_user before each test."""
        self.user = self.create_superuser()
        self.anonymous_user = AnonymousUser()

    def create_superuser(self) -> User:  # type: ignore
        """Create and return a Django superuser.

        Returns:
            User: A Django superuser instance.
        """
        return User.objects.create_superuser("admin", "admin@test.com", "password")

    def assertDateEqual(self, dt_str: str, dt: datetime) -> None:
        """Asserts that the given datetime object matches the provided string representation.

        Args:
            dt_str: the string representation in the format "%Y-%m-%dT%H:%M:%S.%fZ".
            dt: the datetime object to compare.
        """
        self.assertEqual(dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), dt_str)


class BaseApiTest(APITestCase, BaseTestCase):
    """A test case class for testing API functionality."""

    def setUp(self) -> None:
        """Set up the test environment with factory before each test."""
        super().setUp()

        self.factory = APIRequestFactory(enforce_csrf_checks=False)


class BaseAdminTest(BaseApiTest):
    """A test case class for testing admin functionality."""

    def setUp(self) -> None:
        """Set up the test environment with admin site before each test."""
        super().setUp()

        self.site = AdminSite()
        self.client.force_login(self.user)
        self.request = self.factory.get("/")
        self.request.user = self.user

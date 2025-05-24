# pylint: disable=missing-function-docstring

from django.urls import reverse
from rest_framework import status

from compyle.lib.test import BaseAdminTest
from compyle.proxy import admin, models
from compyle.proxy.tests.factories import get_authentication, get_trace

authentication_admin_changelist_url = reverse("admin:proxy_authentication_changelist")
authentication_admin_change_url = lambda pk: reverse("admin:proxy_authentication_change", args=(pk,))
authentication_admin_add_url = reverse("admin:proxy_authentication_add")
endpoint_admin_delete_url = lambda pk: reverse("admin:proxy_authentication_delete", args=(pk,))  # noqa: E731


class AuthenticationAdminTest(BaseAdminTest):
    """Test the admin for the :model:`compyle.proxy.models.Authentication`."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()
        self.auth_admin = admin.AuthenticationAdmin(models.Authentication, self.site)
        self.change_read_only_fields = {
            "reference",
            "is_token_valid",
            "created_at",
            "updated_at",
        }
        self.list_filter_fields = {
            "created_at",
            "updated_at",
        }
        self.payload = {
            "email": "user@example.com",
            "api_key": "sample_api_key",
            "login": "userlogin",
            "password": "secret",
            "client_id": "clientid123",
            "client_secret": "secret123",
            "access_token": "tokenabc",
            "refresh_token": "refresh123",
            "expires_at": "2030-01-01T00:00",
            "auth_traces-TOTAL_FORMS": "0",
            "auth_traces-INITIAL_FORMS": "0",
            "auth_traces-MIN_NUM_FORMS": "0",
            "auth_traces-MAX_NUM_FORMS": "1000",
        }

    def test_can_add_authentication(self) -> None:
        self.assertTrue(self.auth_admin.has_add_permission(self.request))

    def test_can_add_authentication_form_submission(self) -> None:
        response = self.client.post(authentication_admin_add_url, self.payload, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(models.Authentication.objects.count(), 1)
        self.assertEqual(response.context["cl"].result_list[0].email, self.payload["email"])

    def test_cannot_add_authentication_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.post(authentication_admin_add_url, self.payload, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_can_update_authentication(self) -> None:
        self.assertTrue(self.auth_admin.has_change_permission(self.request))

    def test_can_update_authentication_form_submission(self) -> None:
        authentication = get_authentication()

        response = self.client.post(authentication_admin_change_url(authentication.pk), self.payload, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        authentication.refresh_from_db()
        self.assertEqual(authentication.email, self.payload["email"])

    def test_cannot_update_authentication_as_non_staff_user(self) -> None:
        authentication = get_authentication()

        self.client.logout()
        response = self.client.post(authentication_admin_change_url(authentication.pk), self.payload, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_can_delete_authentication(self) -> None:
        self.assertTrue(self.auth_admin.has_delete_permission(self.request))

    def test_can_delete_authentication_form_submission(self) -> None:
        authentication = get_authentication()

        response = self.client.post(endpoint_admin_delete_url(authentication.pk), {"post": "yes"}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(models.Authentication.objects.count(), 0)

    def test_cannot_delete_authentication_as_non_staff_user(self) -> None:
        authentication = get_authentication()

        self.client.logout()
        response = self.client.post(endpoint_admin_delete_url(authentication.pk), {"post": "yes"}, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertTrue(models.Authentication.objects.filter(pk=authentication.pk).exists())
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_get_readonly_fields(self) -> None:
        self.assertSetEqual(set(self.auth_admin.get_readonly_fields(self.request)), self.change_read_only_fields)

    def test_list_filter_fields(self) -> None:
        self.assertSetEqual(set(self.auth_admin.list_filter), {"created_at", "updated_at"})

    def test_can_list_authentications(self) -> None:
        authentications = [get_authentication() for _ in range(3)]

        response = self.client.get(authentication_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), len(authentications))

    def test_cannot_list_authentications_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.get(authentication_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

    def test_can_list_authentications_search_by_reference(self) -> None:
        authentications = [get_authentication() for _ in range(3)]
        reference = authentications[0].reference

        response = self.client.get(authentication_admin_changelist_url, {"q": reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertEqual(response.context["cl"].result_list[0].reference, reference)

    def test_can_list_authentications_search_by_partial_reference(self) -> None:
        authentications = [get_authentication() for _ in range(3)]

        response = self.client.get(authentication_admin_changelist_url, {"q": "-authentication-"})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), len(authentications))

    def test_can_list_authentications_search_by_trace_endpoint_reference(self) -> None:
        authentications = [get_authentication() for _ in range(3)]
        trace = get_trace(authentication=authentications[0])

        response = self.client.get(authentication_admin_changelist_url, {"q": trace.endpoint.reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertEqual(response.context["cl"].result_list[0].reference, authentications[0].reference)

    def test_can_list_authentications_search_by_trace_endpoint_partial_reference(self) -> None:
        authentications = [get_authentication() for _ in range(3)]
        _ = get_trace(authentication=authentications[0])

        response = self.client.get(authentication_admin_changelist_url, {"q": "-endpoint-"})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertEqual(response.context["cl"].result_list[0].reference, authentications[0].reference)

    def test_can_consult_authentication(self) -> None:
        authentication = get_authentication()

        response = self.client.get(authentication_admin_change_url(authentication.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertContains(response, authentication.pk)

    def test_cannot_consult_authentication_as_non_staff_user(self) -> None:
        authentication = get_authentication()

        self.client.logout()
        response = self.client.get(authentication_admin_change_url(authentication.pk))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

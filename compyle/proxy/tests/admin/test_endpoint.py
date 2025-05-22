# pylint: disable=missing-function-docstring

from unittest import mock

from django.contrib import messages
from django.urls import reverse
from rest_framework import status

from compyle.lib.test import BaseAdminTest
from compyle.proxy import admin, choices, forms, models
from compyle.proxy.tests.factories import get_authentication, get_endpoint, get_service

endpoint_admin_changelist_url = reverse("admin:proxy_endpoint_changelist")
endpoint_admin_change_url = lambda pk: reverse("admin:proxy_endpoint_change", args=(pk,))  # noqa: E731
endpoint_admin_add_url = reverse("admin:proxy_endpoint_add")
endpoint_admin_delete_url = lambda pk: reverse("admin:proxy_endpoint_delete", args=(pk,))  # noqa: E731

endpoint_admin_request_url = lambda pk: reverse("admin:proxy_endpoint_actions", args=(pk, "retry"))  # noqa: E731


class EndpointAdminTest(BaseAdminTest):
    """Test the admin for the :model:`compyle.proxy.models.Endpoint`."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

        self.endpoint_admin = admin.EndpointAdmin(models.Endpoint, self.site)
        self.change_read_only_fields = {
            "reference",
            "created_at",
            "updated_at",
        }
        self.list_filter_fields = {
            "created_at",
            "updated_at",
        }
        self.payload = {
            "name": "ENDPOINT_NAME_001",
            "method": choices.HttpMethod.GET.value,
            "base_url": "https://api.example.com",
            "slug": "test-endpoint",
            "service": get_service().pk,
            "response_type": choices.ResponseType.JSON.value,
            "endpoint_traces-TOTAL_FORMS": "0",
            "endpoint_traces-INITIAL_FORMS": "0",
        }

    def test_can_add_endpoint(self) -> None:
        self.assertTrue(self.endpoint_admin.has_add_permission(self.request))

    def test_can_add_endpoint_form_submission(self) -> None:
        response = self.client.post(endpoint_admin_add_url, self.payload, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(models.Endpoint.objects.count(), 1)
        self.assertEqual(response.context["cl"].result_list[0].name, self.payload["name"])

    def test_cannot_add_endpoint_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.post(endpoint_admin_add_url, self.payload, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_can_update_endpoint(self) -> None:
        self.assertTrue(self.endpoint_admin.has_change_permission(self.request))

    def test_can_update_endpoint_form_submission(self) -> None:
        endpoint = get_endpoint()

        response = self.client.post(endpoint_admin_change_url(endpoint.pk), self.payload, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)

        endpoint.refresh_from_db()
        self.assertEqual(endpoint.name, self.payload["name"])
        self.assertEqual(response.context["cl"].result_list[0].name, self.payload["name"])

    def test_cannot_update_endpoint_as_non_staff_user(self) -> None:
        endpoint = get_endpoint()

        self.client.logout()
        response = self.client.post(endpoint_admin_change_url(endpoint.pk), self.payload, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_can_delete_endpoint(self) -> None:
        self.assertTrue(self.endpoint_admin.has_delete_permission(self.request))

    def test_can_delete_endpoint_form_submission(self) -> None:
        endpoint = get_endpoint()
        response = self.client.post(endpoint_admin_delete_url(endpoint.pk), {"post": "yes"}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(models.Endpoint.objects.count(), 0)

    def test_cannot_delete_endpoint_as_non_staff_user(self) -> None:
        endpoint = get_endpoint()
        self.client.logout()

        response = self.client.post(endpoint_admin_delete_url(endpoint.pk), {"post": "yes"}, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )
        self.assertTrue(models.Endpoint.objects.filter(pk=endpoint.pk).exists())

    def test_get_endpoint_readonly_fields(self) -> None:
        self.assertSetEqual(set(self.endpoint_admin.get_readonly_fields(self.request)), self.change_read_only_fields)

    def test_get_endpoint_filter_fields(self) -> None:
        self.assertSetEqual(set(self.endpoint_admin.get_list_filter(self.request)), self.list_filter_fields)

    def test_endpoint_ordering(self) -> None:
        endpoints = [get_endpoint() for _ in range(3)]
        response = self.client.get(endpoint_admin_changelist_url)

        self.assertCountEqual(
            [e.reference for e in response.context["cl"].result_list],
            [e.reference for e in endpoints],
        )
        self.assertTrue(
            all(
                response.context["cl"].result_list[i - 1].updated_at >= e.updated_at
                for i, e in enumerate(response.context["cl"].result_list, start=1)
            )
        )

    def test_can_list_endpoints(self) -> None:
        endpoints = [get_endpoint() for _ in range(3)]

        response = self.client.get(endpoint_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), len(endpoints))

    def test_cannot_list_endpoints_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.get(endpoint_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

    def test_can_list_endpoints_search_by_reference(self) -> None:
        endpoints = [get_endpoint() for _ in range(3)]
        reference = endpoints[0].reference

        response = self.client.get(endpoint_admin_changelist_url, {"q": reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertEqual(response.context["cl"].result_list[0].reference, reference)

    def test_can_list_endpoints_search_by_name(self) -> None:
        endpoints = [
            get_endpoint(name="Google Maps"),
            get_endpoint(name="Google Translate"),
            get_endpoint(name="OpenAI"),
        ]
        name = "Google Maps"

        response = self.client.get(endpoint_admin_changelist_url, {"q": name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertCountEqual(
            [endpoint.reference for endpoint in response.context["cl"].result_list],
            [endpoint.reference for endpoint in endpoints if name == endpoint.name],
        )

    def test_can_list_endpoints_search_by_partial_name(self) -> None:
        endpoints = [
            get_endpoint(name="Google Maps"),
            get_endpoint(name="Google Translate"),
            get_endpoint(name="OpenAI"),
        ]
        partial_name = "Google"

        response = self.client.get(endpoint_admin_changelist_url, {"q": partial_name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [endpoint.reference for endpoint in response.context["cl"].result_list],
            [endpoint.reference for endpoint in endpoints if partial_name in endpoint.name],
        )

    def test_can_list_endpoints_search_by_service_reference(self) -> None:
        service = get_service()
        endpoints = [get_endpoint(service=service), get_endpoint(service=service), get_endpoint()]

        response = self.client.get(endpoint_admin_changelist_url, {"q": service.reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [endpoint.reference for endpoint in response.context["cl"].result_list],
            [endpoint.reference for endpoint in endpoints if endpoint.service.reference == service.reference],
        )

    def test_can_list_endpoints_search_by_service_name(self) -> None:
        service = get_service()
        endpoints = [get_endpoint(service=service), get_endpoint(service=service), get_endpoint()]

        response = self.client.get(endpoint_admin_changelist_url, {"q": service.name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [endpoint.reference for endpoint in response.context["cl"].result_list],
            [endpoint.reference for endpoint in endpoints if endpoint.service.name == service.name],
        )

    def test_can_list_endpoints_search_by_service_partial_name(self) -> None:
        service = get_service(name="Youtube v1")
        endpoints = [get_endpoint(service=service), get_endpoint(service=service), get_endpoint()]
        partial_name = "tube"

        response = self.client.get(endpoint_admin_changelist_url, {"q": partial_name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [endpoint.reference for endpoint in response.context["cl"].result_list],
            [endpoint.reference for endpoint in endpoints if partial_name in endpoint.service.name],
        )

    def test_can_consult_endpoint(self) -> None:
        endpoint = get_endpoint()

        response = self.client.get(endpoint_admin_change_url(endpoint.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertContains(response, endpoint.pk)

    def test_cannot_consult_endpoint_as_non_staff_user(self) -> None:
        endpoint = get_endpoint()

        self.client.logout()
        response = self.client.get(endpoint_admin_change_url(endpoint.pk))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

    @mock.patch("compyle.proxy.admin.EndpointAdmin.message_user")
    @mock.patch("compyle.proxy.admin.async_request.delay")
    def test_can_request_endpoint(
        self,
        mock_task: mock.MagicMock,
        mock_message_user: mock.MagicMock,
    ) -> None:
        authentication = get_authentication()
        endpoint = get_endpoint()

        form_data = {
            "authentication": authentication.pk,
            "params": '{"q": "test"}',
            "headers": '{"Authorization": "Bearer token"}',
            "payload": '{"data": "value"}',
        }

        mock_request = mock.MagicMock(user=self.user)
        form = forms.TraceForm(instance=endpoint, data=form_data)

        self.assertTrue(form.is_valid())

        request_action = self.endpoint_admin.request.__wrapped__.__wrapped__
        request_action(self.endpoint_admin, mock_request, endpoint, form)

        mock_task.assert_called_once_with(
            endpoint.reference,
            authentication.pk,
            {"q": "test"},
            {"Authorization": "Bearer token"},
            {"data": "value"},
            timeout=mock.ANY,
        )
        mock_message_user.assert_called_once_with(mock_request, mock.ANY, messages.SUCCESS)

    @mock.patch("compyle.proxy.admin.EndpointAdmin.message_user")
    @mock.patch("compyle.proxy.admin.async_request.delay")
    def test_can_request_endpoint_without_authentication(
        self,
        mock_task: mock.MagicMock,
        mock_message_user: mock.MagicMock,
    ) -> None:
        endpoint = get_endpoint()

        form_data = {
            "params": '{"q": "test"}',
            "headers": '{"Authorization": "Bearer token"}',
            "payload": '{"data": "value"}',
        }

        mock_request = mock.MagicMock(user=self.user)
        form = forms.TraceForm(instance=endpoint, data=form_data)

        self.assertTrue(form.is_valid())

        request_action = self.endpoint_admin.request.__wrapped__.__wrapped__
        request_action(self.endpoint_admin, mock_request, endpoint, form)

        mock_task.assert_called_once_with(
            endpoint.reference,
            None,
            {"q": "test"},
            {"Authorization": "Bearer token"},
            {"data": "value"},
            timeout=mock.ANY,
        )
        mock_message_user.assert_called_once_with(mock_request, mock.ANY, messages.SUCCESS)

    @mock.patch("compyle.proxy.admin.EndpointAdmin.message_user")
    @mock.patch("compyle.proxy.admin.async_request.delay", side_effect=Exception())
    def test_can_request_endpoint_action_failure(
        self,
        mock_task: mock.MagicMock,
        mock_message_user: mock.MagicMock,
    ) -> None:
        endpoint = get_endpoint()

        form_data = {}

        mock_request = mock.MagicMock(user=self.user)
        form = forms.TraceForm(instance=endpoint, data=form_data)

        self.assertTrue(form.is_valid())

        request_action = self.endpoint_admin.request.__wrapped__.__wrapped__
        request_action(self.endpoint_admin, mock_request, endpoint, form)

        mock_task.assert_called_once()
        mock_message_user.assert_called_once_with(mock_request, mock.ANY, messages.ERROR)

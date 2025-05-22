# pylint: disable=missing-function-docstring

from django.urls import reverse
from rest_framework import status

from compyle.lib.test import BaseAdminTest
from compyle.proxy import admin, models
from compyle.proxy.tests.factories import get_service

service_admin_changelist_url = reverse("admin:proxy_service_changelist")
service_admin_change_url = lambda pk: reverse("admin:proxy_service_change", args=(pk,))  # noqa: E731
service_admin_add_url = reverse("admin:proxy_service_add")


class ServiceAdminTest(BaseAdminTest):
    """Test the admin for the :model:`compyle.proxy.models.Service`."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

        self.service_admin = admin.ServiceAdmin(models.Service, self.site)
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
            "name": "SERVICE_NAME_001",
            "endpoints-TOTAL_FORMS": "0",
            "endpoints-INITIAL_FORMS": "0",
            "endpoints-MIN_NUM_FORMS": "0",
            "endpoints-MAX_NUM_FORMS": "1000",
        }

    def test_can_add_service(self) -> None:
        self.assertTrue(self.service_admin.has_add_permission(self.request))

    def test_can_add_service_form_submission(self) -> None:
        response = self.client.post(service_admin_add_url, self.payload, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(models.Service.objects.count(), 1)
        self.assertEqual(response.context["cl"].result_list[0].name, self.payload["name"])

    def test_cannot_add_service_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.post(service_admin_add_url, self.payload, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND))
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_can_update_service(self) -> None:
        self.assertTrue(self.service_admin.has_change_permission(self.request))

    def test_can_update_service_form_submission(self) -> None:
        service = get_service()

        response = self.client.post(service_admin_change_url(service.pk), self.payload, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)

        service.refresh_from_db()
        self.assertEqual(service.name, self.payload["name"])
        self.assertEqual(response.context["cl"].result_list[0].name, self.payload["name"])

    def test_cannot_update_service_as_non_staff_user(self) -> None:
        service = get_service()

        self.client.logout()
        response = self.client.post(service_admin_change_url(service.pk), self.payload, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_can_delete_service(self) -> None:
        self.assertTrue(self.service_admin.has_delete_permission(self.request))

    def test_can_delete_service_form_submission(self) -> None:
        service = get_service()

        response = self.client.post(service_admin_change_url(service.pk), {"post": "yes"}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertTrue(models.Service.objects.count(), 0)

    def test_cannot_delete_service_as_non_staff_user(self) -> None:
        service = get_service()
        self.client.logout()

        response = self.client.post(service_admin_change_url(service.pk), {"post": "yes"}, follow=True)

        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND), response.reason_phrase)
        self.assertTrue(models.Service.objects.filter(pk=service.pk).exists())
        self.assertIn(
            "/admin/login/", response.redirect_chain[0][0] if response.redirect_chain else response.request["PATH_INFO"]
        )

    def test_get_service_readonly_fields(self) -> None:
        self.assertSetEqual(set(self.service_admin.get_readonly_fields(self.request)), self.change_read_only_fields)

    def test_get_services_filter_fields(self):
        self.assertSetEqual(set(self.service_admin.get_list_filter(self.request)), self.list_filter_fields)

    def test_services_ordering(self) -> None:
        services = [get_service() for _ in range(3)]

        response = self.client.get(service_admin_changelist_url)

        self.assertCountEqual(
            [service.reference for service in response.context["cl"].result_list],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.context["cl"].result_list[i - 1].reference >= service.reference
                for i, service in enumerate(response.context["cl"].result_list, start=1)
            )
        )

    def test_can_list_services(self) -> None:
        services = [get_service() for _ in range(3)]

        response = self.client.get(service_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), len(services))

    def test_cannot_list_services_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.get(service_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

    def test_can_list_services_search_by_reference(self) -> None:
        services = [get_service() for _ in range(3)]
        reference = services[0].reference

        response = self.client.get(service_admin_changelist_url, {"q": reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertTrue(response.context["cl"].result_list[0].reference, reference)

    def test_can_list_services_search_by_partial_reference(self) -> None:
        services = [get_service() for _ in range(3)]

        response = self.client.get(service_admin_changelist_url, {"q": "-service-"})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), len(services))

    def test_can_list_services_search_by_name(self) -> None:
        services = [get_service(name="Youtube"), get_service(name="Twitch"), get_service(name="Twitch")]
        name = "Twitch"

        response = self.client.get(service_admin_changelist_url, {"q": name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [service.reference for service in response.context["cl"].result_list],
            [service.reference for service in services if name == service.name],
        )

    def test_can_list_services_search_by_partial_name(self) -> None:
        services = [get_service(name="Youtube v1"), get_service(name="Youtube v2"), get_service(name="Twitch")]
        partial_name = "Youtube"

        response = self.client.get(service_admin_changelist_url, {"q": partial_name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [service.reference for service in response.context["cl"].result_list],
            [service.reference for service in services if partial_name in service.name],
        )

    def test_can_consult_service(self) -> None:
        service = get_service()

        response = self.client.get(service_admin_change_url(service.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertContains(response, service.pk)

    def test_cannot_consult_service_as_non_staff_user(self) -> None:
        service = get_service()

        self.client.logout()
        response = self.client.get(service_admin_change_url(service.pk))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

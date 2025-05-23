# pylint: disable=missing-function-docstring, too-many-public-methods

import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate

from compyle.lib.test import BaseApiTest
from compyle.proxy.models import Endpoint, Service
from compyle.proxy.tests.factories import get_endpoint, get_service
from compyle.proxy.views import ServiceViewSet

list_url = reverse("proxy:services-list")
list_view = ServiceViewSet.as_view({"get": "list", "post": "create"})

detail_url = reverse("proxy:services-detail", kwargs={"pk": None})
detail_view = ServiceViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)


class ServiceTestCase(BaseApiTest):
    """TestCase for :class:`comprle.proxy.views.ServiceViewSet`."""

    # pylint: disable=invalid-name
    def setUp(self) -> None:
        super().setUp()

        self.minimal_payload = {
            "name": "SERVICE_NAME_001",
        }

    def test_can_list_services(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url)
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )

    def test_can_list_services_search_by_reference(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"search": services[0].reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["results"][0]["reference"], services[0].reference)

    def test_can_list_services_search_by_name(self) -> None:
        services = [get_service(name="name1"), get_service(name="name1"), get_service(name="name2")]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"search": services[0].name})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services if service.name == services[0].name],
        )

    def test_can_list_services_order_asc_by_reference(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "reference"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["reference"] <= service["reference"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_desc_by_reference(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-reference"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["reference"] >= service["reference"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_asc_by_created_at(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "created_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["created_at"] <= service["created_at"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_desc_by_created_at(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-created_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["created_at"] >= service["created_at"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_asc_by_updated_at(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "updated_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["updated_at"] <= service["updated_at"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_desc_by_updated_at(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-updated_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["updated_at"] >= service["updated_at"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_asc_by_name(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "name"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["name"] <= service["name"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_order_desc_by_name(self) -> None:
        services = [get_service() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-name"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            [service.reference for service in services],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["name"] >= service["name"]
                for i, service in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_services_filter_by_reference(self) -> None:
        services = [get_service() for _ in range(5)]
        reference = services[0].reference

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"references": reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["reference"], reference)

    def test_can_list_services_filter_by_references(self) -> None:
        services = [get_service() for _ in range(5)]
        references = [service.reference for service in services[:2]]

        with self.assertNumQueries(3):
            data = {"references": ",".join(references)}
            request = self.factory.get(list_url, data=data)
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual(
            [service["reference"] for service in response.data["results"]],
            references,
        )

    def test_can_retrieve_service(self) -> None:
        service = get_service()

        with self.assertNumQueries(2):
            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], service.reference)
        self.assertEqual(response.data["name"], service.name)
        self.assertEqual(response.data["trailing_slash"], service.trailing_slash)
        self.assertEqual(response.data["auth_flow"], service.auth_flow)
        self.assertEqual(response.data["endpoints"], [])
        self.assertDateEqual(response.data["created_at"], service.created_at)
        self.assertDateEqual(response.data["updated_at"], service.updated_at)

    def test_cannot_retrieve_unknown_service(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_can_create_service(self) -> None:
        with self.assertNumQueries(4):
            request = self.factory.post(list_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Service.objects.count(), 1)

        self.assertEqual(response.data["name"], self.minimal_payload["name"])
        self.assertIsNone(response.data["auth_flow"])
        self.assertIsNone(response.data["token_url"])

    def test_can_create_service_with_endpoint(self) -> None:
        payload = self.minimal_payload
        payload["endpoints"] = [
            {
                "name": "ENDPOINT_NAME_001",
                "base_url": "https://api.twitch.tv/helix",
                "slug": "/games",
                "method": "get",
            }
        ]

        with self.assertNumQueries(6):
            request = self.factory.post(list_url, payload, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Endpoint.objects.count(), 1)

        service, endpoint = Service.objects.first(), Endpoint.objects.first()
        self.assertEqual(endpoint.service.reference, service.reference)

        self.assertEqual(response.data["reference"], service.reference)
        self.assertEqual(response.data["name"], payload["name"])
        self.assertEqual(response.data["endpoints"][0]["reference"], endpoint.reference)
        self.assertEqual(response.data["endpoints"][0]["name"], payload["endpoints"][0]["name"])
        self.assertEqual(response.data["endpoints"][0]["base_url"], payload["endpoints"][0]["base_url"])
        self.assertEqual(response.data["endpoints"][0]["slug"], payload["endpoints"][0]["slug"])
        self.assertEqual(response.data["endpoints"][0]["method"], payload["endpoints"][0]["method"])

    def test_can_create_service_with_endpoints(self) -> None:
        payload = self.minimal_payload
        payload["endpoints"] = [
            {
                "name": "ENDPOINT_NAME_001",
                "base_url": "https://api.twitch.tv/helix",
                "slug": "/games",
                "method": "get",
            },
            {
                "name": "ENDPOINT_NAME_002",
                "base_url": "https://api.twitch.tv/helix",
                "slug": "/clips",
                "method": "get",
            },
        ]

        with self.assertNumQueries(7):
            request = self.factory.post(list_url, payload, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Endpoint.objects.count(), 2)

        service, endpoints = Service.objects.first(), Endpoint.objects.all()
        self.assertTrue(all(service.reference == endpoint.service.reference for endpoint in endpoints))

        self.assertEqual(response.data["reference"], service.reference)
        self.assertEqual(response.data["name"], payload["name"])
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["endpoints"]],
            [endpoint.reference for endpoint in endpoints],
        )

    def test_cannot_create_service_as_anonymous_user(self) -> None:
        with self.assertNumQueries(0):
            request = self.factory.post(list_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.anonymous_user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_can_partial_update_service(self) -> None:
        service = get_service()

        with self.assertNumQueries(4):
            request = self.factory.patch(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], service.reference)
        self.assertEqual(response.data["name"], self.minimal_payload["name"])
        self.assertEqual(response.data["trailing_slash"], service.trailing_slash)
        self.assertEqual(response.data["auth_flow"], service.auth_flow)
        self.assertEqual(response.data["token_url"], service.token_url)
        self.assertEqual(response.data["endpoints"], [])

    def test_cannot_partial_update_service_as_anonymous_user(self) -> None:
        service = get_service()

        with self.assertNumQueries(0):
            request = self.factory.patch(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.anonymous_user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_cannot_partial_update_unknown_service(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.patch(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_cannot_update_service_as_anonymous_user(self) -> None:
        service = get_service()

        with self.assertNumQueries(0):
            request = self.factory.put(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.anonymous_user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_cannot_update_unknown_service(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.put(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_can_update_service(self) -> None:
        service = get_service()

        with self.assertNumQueries(4):
            request = self.factory.put(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], service.reference)
        self.assertEqual(response.data["name"], self.minimal_payload["name"])

    def test_cannot_delete_service_as_anonymous_user(self) -> None:
        service = get_service()

        with self.assertNumQueries(0):
            request = self.factory.delete(detail_url)
            force_authenticate(request, user=self.anonymous_user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_cannot_delete_unknown_service(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.delete(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_can_delete_service(self) -> None:
        service = get_service()

        with self.assertNumQueries(4):
            request = self.factory.delete(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=service.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertEqual(Service.objects.count(), 0)

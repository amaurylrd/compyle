# pylint: disable=missing-function-docstring, too-many-public-methods

import uuid
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate

from compyle.lib.test import BaseApiTest
from compyle.proxy.models import Endpoint
from compyle.proxy.tests.factories import get_authentication, get_endpoint, get_service
from compyle.proxy.views import EndpointViewSet

list_url = reverse("proxy:endpoints-list")
list_view = EndpointViewSet.as_view({"get": "list", "post": "create"})

detail_url = reverse("proxy:endpoints-detail", kwargs={"pk": None})
detail_view = EndpointViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

request_url = reverse("proxy:endpoints-request", kwargs={"pk": None})
request_view = EndpointViewSet.as_view({"post": "trigger_request"})


class EndpointTest(BaseApiTest):
    """TestCase for :class:`comprle.proxy.views.EndpointViewSet`."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

        self.minimal_payload = {
            "service": get_service().reference,
            "name": "ENDPOINT_NAME_001",
            "base_url": "https://api.twitch.tv/helix",
            "slug": "/games",
            "method": "get",
        }

    def test_can_list_endpoints(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url)
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )

    def test_can_list_endpoints_search_by_reference(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"search": endpoints[0].reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["results"][0]["reference"], endpoints[0].reference)

    def test_can_list_endpoints_search_by_name(self) -> None:
        endpoints = [get_endpoint(name="name1"), get_endpoint(name="name1"), get_endpoint(name="name2")]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"search": endpoints[0].name})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints if endpoint.name == endpoints[0].name],
        )

    def test_can_list_endpoints_search_by_service_reference(self) -> None:
        service = get_service()
        endpoints = [get_endpoint(service=service), get_endpoint(service=service), get_endpoint()]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"search": service.reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints[:2]],
        )

    def test_can_list_endpoints_order_asc_by_reference(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "reference"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["reference"] <= endpoint["reference"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_desc_by_reference(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-reference"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["reference"] >= endpoint["reference"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_asc_by_created_at(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "created_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["created_at"] <= endpoint["created_at"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_desc_by_created_at(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-created_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["created_at"] >= endpoint["created_at"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_asc_by_updated_at(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "updated_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["updated_at"] <= endpoint["updated_at"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_desc_by_updated_at(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-updated_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["updated_at"] >= endpoint["updated_at"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_asc_by_name(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "name"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["name"] <= endpoint["name"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_order_desc_by_name(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"ordering": "-name"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            [endpoint.reference for endpoint in endpoints],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["name"] >= endpoint["name"]
                for i, endpoint in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_endpoints_filter_by_reference(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]
        reference = endpoints[0].reference

        with self.assertNumQueries(3):
            request = self.factory.get(list_url, data={"references": reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["reference"], reference)

    def test_can_list_endpoints_filter_by_references(self) -> None:
        endpoints = [get_endpoint() for _ in range(5)]
        references = [endpoint.reference for endpoint in endpoints[:2]]

        with self.assertNumQueries(3):
            data = {"references": ",".join(references)}
            request = self.factory.get(list_url, data=data)
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual(
            [endpoint["reference"] for endpoint in response.data["results"]],
            references,
        )

    def test_can_retrieve_endpoint(self) -> None:
        endpoint = get_endpoint()

        with self.assertNumQueries(2):
            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], endpoint.reference)
        self.assertEqual(response.data["name"], endpoint.name)
        self.assertEqual(response.data["base_url"], endpoint.base_url)
        self.assertEqual(response.data["slug"], endpoint.slug)
        self.assertEqual(response.data["method"], endpoint.method)
        self.assertEqual(response.data["response_type"], endpoint.response_type)
        self.assertEqual(response.data["auth_method"], endpoint.auth_method)
        self.assertEqual(response.data["service"], endpoint.service.reference)
        self.assertEqual(response.data["traces"], [])
        self.assertDateEqual(response.data["created_at"], endpoint.created_at)
        self.assertDateEqual(response.data["updated_at"], endpoint.updated_at)

    def test_cannot_retrieve_unknown_endpoint(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_can_create_endpoint(self) -> None:
        with self.assertNumQueries(3):
            request = self.factory.post(list_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Endpoint.objects.count(), 1)

        endpoint = Endpoint.objects.first()

        self.assertEqual(response.data["reference"], endpoint.reference)
        self.assertEqual(response.data["name"], self.minimal_payload["name"])
        self.assertEqual(response.data["base_url"], self.minimal_payload["base_url"])
        self.assertEqual(response.data["slug"], self.minimal_payload["slug"])
        self.assertEqual(response.data["method"], self.minimal_payload["method"])

    def cannot_create_endpoint_without_service(self) -> None:
        self.minimal_payload.pop("service")

        with self.assertNumQueries(5):
            request = self.factory.post(list_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(Endpoint.objects.count(), 0)

    def cannot_create_endpoint_with_unkown_service(self) -> None:
        self.minimal_payload["service"] = str(uuid.uuid4())

        with self.assertNumQueries(5):
            request = self.factory.post(list_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(Endpoint.objects.count(), 0)

    def test_cannot_create_endpoint_as_anonymous_user(self) -> None:
        with self.assertNumQueries(0):
            request = self.factory.post(list_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.anonymous_user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        self.assertEqual(Endpoint.objects.count(), 0)

    def test_can_partial_update_endpoint(self) -> None:
        endpoint = get_endpoint()
        payload = {
            "name": "ENDPOINT_NAME_001",
        }

        with self.assertNumQueries(4):
            request = self.factory.patch(detail_url, payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], endpoint.reference)
        self.assertEqual(response.data["name"], payload["name"])

    def test_cannot_partial_update_unknown_endpoint(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.patch(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_cannot_partial_update_endpoint_as_anonymous_user(self) -> None:
        endpoint = get_endpoint()

        with self.assertNumQueries(0):
            request = self.factory.patch(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.anonymous_user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_can_update_service(self) -> None:
        endpoint = get_endpoint()
        payload = {
            "service": endpoint.service.reference,
            "name": "ENDPOINT_NAME_001",
            "base_url": endpoint.base_url,
            "slug": endpoint.slug,
            "method": endpoint.method,
        }

        with self.assertNumQueries(5):
            request = self.factory.put(detail_url, payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], endpoint.reference)
        self.assertEqual(response.data["service"], endpoint.service.reference)
        self.assertEqual(response.data["name"], self.minimal_payload["name"])
        self.assertEqual(response.data["base_url"], endpoint.base_url)
        self.assertEqual(response.data["slug"], endpoint.slug)
        self.assertEqual(response.data["method"], endpoint.method)

    def test_cannot_update_endpoint_as_anonymous_user(self) -> None:
        endpoint = get_endpoint()

        with self.assertNumQueries(0):
            request = self.factory.put(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.anonymous_user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_cannot_update_unknown_endpoint(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.put(detail_url, self.minimal_payload, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_cannot_delete_endpoint_as_anonymous_user(self) -> None:
        endpoint = get_endpoint()

        with self.assertNumQueries(0):
            request = self.factory.delete(detail_url)
            force_authenticate(request, user=self.anonymous_user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        self.assertTrue(Endpoint.objects.filter(pk=endpoint.pk).exists())

    def test_cannot_delete_unknown_endpoint(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.delete(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_can_delete_endpoint(self) -> None:
        endpoint = get_endpoint()

        with self.assertNumQueries(4):
            request = self.factory.delete(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=endpoint.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertEqual(Endpoint.objects.count(), 0)

    @mock.patch("compyle.proxy.views.async_request")
    def test_can_request_endpoint_with_empty_payload(self, mock_async_request: mock.MagicMock) -> None:
        endpoint = get_endpoint()
        payload = {}

        mock_task_result = mock.MagicMock()
        mock_task_result.id = str(uuid.uuid4())
        mock_async_request.delay.return_value = mock_task_result

        with self.assertNumQueries(2):
            request = self.factory.post(request_url, payload, format="json")
            force_authenticate(request, user=self.user)
            response = request_view(request, pk=endpoint.pk)

        mock_async_request.delay.assert_called_once_with(
            endpoint.reference,
            None,
            {},
            {},
            None,
            timeout=None,
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED, response.data)
        self.assertEqual(response.data["task_id"], mock_task_result.id)

    @mock.patch("compyle.proxy.views.async_request")
    def test_can_request_endpoint(self, mock_async_request: mock.MagicMock) -> None:
        endpoint = get_endpoint()
        authentication = get_authentication()
        payload = {
            "authentication": authentication.reference,
            "params": {"query": "test"},
            "headers": {"Accept": "application/json"},
            "body": {"data": "example"},
            "timeout": 60,
        }

        mock_task_result = mock.MagicMock()
        mock_task_result.id = str(uuid.uuid4())
        mock_async_request.delay.return_value = mock_task_result

        with self.assertNumQueries(3):
            request = self.factory.post(request_url, payload, format="json")
            force_authenticate(request, user=self.user)
            response = request_view(request, pk=endpoint.pk)

        mock_async_request.delay.assert_called_once_with(
            endpoint.reference,
            authentication.reference,
            payload["params"],
            payload["headers"],
            payload["body"],
            timeout=float(payload["timeout"]),
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED, response.data)
        self.assertEqual(response.data["task_id"], mock_task_result.id)

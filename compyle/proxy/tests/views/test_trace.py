# pylint: disable=missing-function-docstring, too-many-public-methods

import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate

from compyle.lib.test import BaseApiTest
from compyle.proxy.tests.factories import get_authentication, get_endpoint, get_trace
from compyle.proxy.views import TraceViewSet

list_url = reverse("proxy:services-list")
list_view = TraceViewSet.as_view({"get": "list"})

detail_url = reverse("proxy:services-detail", kwargs={"pk": None})
detail_view = TraceViewSet.as_view({"get": "retrieve"})


class TraceTest(BaseApiTest):
    """TestCase for :class:`comprle.proxy.views.TraceViewSet`."""

    def test_can_list_traces(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url)
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )

    def test_can_list_traces_search_by_reference(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"search": traces[0].reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["results"][0]["reference"], traces[0].reference)

    def test_can_list_trace_search_by_endpoint_reference(self) -> None:
        endpoint = get_endpoint()
        traces = [
            get_trace(endpoint=endpoint),
            get_trace(endpoint=endpoint),
            get_trace(),
        ]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"search": traces[0].endpoint.reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces if trace.endpoint.reference == endpoint.reference],
        )

    def test_can_list_trace_search_by_authentication_reference(self) -> None:
        authentication = get_authentication()
        traces = [
            get_trace(authentication=authentication),
            get_trace(authentication=authentication),
            get_trace(),
        ]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"search": traces[0].authentication.reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces if trace.authentication.reference == authentication.reference],
        )

    def test_can_list_traces_order_asc_by_reference(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "reference"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["reference"] <= trace["reference"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_desc_by_reference(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "-reference"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["reference"] >= trace["reference"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_asc_by_started_at(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "started_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["started_at"] <= trace["started_at"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_desc_by_started_at(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "-started_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["started_at"] >= trace["started_at"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_asc_by_completed_at(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "completed_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["completed_at"] is None
                or response.data["results"][i - 1]["completed_at"] <= trace["completed_at"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_desc_by_completed_at(self) -> None:
        traces = [get_trace() for _ in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "-completed_at"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["completed_at"] is None
                or response.data["results"][i - 1]["completed_at"] >= trace["completed_at"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_asc_by_status_code(self) -> None:
        traces = [get_trace(status_code=i) for i in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "status_code"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["status_code"] <= trace["status_code"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_order_desc_by_status_code(self) -> None:
        traces = [get_trace(status_code=i) for i in range(5)]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"ordering": "-status_code"})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces],
        )
        self.assertTrue(
            all(
                response.data["results"][i - 1]["status_code"] >= trace["status_code"]
                for i, trace in enumerate(response.data["results"], start=1)
            )
        )

    def test_can_list_traces_filter_by_reference(self) -> None:
        traces = [get_trace() for _ in range(5)]
        reference = traces[0].reference

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"references": reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["reference"], reference)

    def test_can_list_traces_filter_by_references(self) -> None:
        traces = [get_trace() for _ in range(5)]
        references = [trace.reference for trace in traces[:2]]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"references": ",".join(references)})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            references,
        )

    def test_can_list_traces_filter_by_endpoint_reference(self) -> None:
        traces = [get_trace() for _ in range(5)]
        reference = traces[0].endpoint.reference

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"endpoints": reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["reference"], traces[0].reference)

    def test_can_list_traces_filter_by_endpoint_references(self) -> None:
        traces = [get_trace() for _ in range(5)]
        references = [trace.endpoint.reference for trace in traces[:2]]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"endpoints": ",".join(references)})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces[:2]],
        )

    def test_can_list_traces_filter_by_service_reference(self) -> None:
        traces = [get_trace() for _ in range(5)]
        reference = traces[0].endpoint.service.reference

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"services": reference})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["reference"], traces[0].reference)

    def test_can_list_traces_filter_by_service_references(self) -> None:
        traces = [get_trace() for _ in range(5)]
        references = [trace.endpoint.service.reference for trace in traces[:2]]

        with self.assertNumQueries(2):
            request = self.factory.get(list_url, data={"services": ",".join(references)})
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces[:2]],
        )

    def test_can_list_traces_filter_by_status_code(self) -> None:
        traces = [get_trace(status_code=i) for i in range(5)]
        status_code = traces[0].status_code

        request = self.factory.get(list_url, {"status_code": status_code})
        force_authenticate(request, user=self.user)
        response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status_code"], status_code)

    def test_can_list_traces_filter_by_status_codes(self) -> None:
        traces = [get_trace(status_code=i) for i in range(5)]
        status_codes = [str(trace.status_code) for trace in traces[:2]]

        request = self.factory.get(list_url, {"status_code": ",".join(status_codes)})
        force_authenticate(request, user=self.user)
        response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces[:2]],
        )

    def test_filter_by_status_code_startswith(self) -> None:
        traces = [get_trace(status_code=200), get_trace(status_code=201), get_trace(status_code=404)]

        request = self.factory.get(list_url, {"status_code_startswith": "2"})
        force_authenticate(request, user=self.user)
        response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(str(trace["status_code"]).startswith("2") for trace in response.data["results"]))
        self.assertCountEqual(
            [trace["reference"] for trace in response.data["results"]],
            [trace.reference for trace in traces[:2]],
        )

    def test_can_retrieve_trace(self) -> None:
        trace = get_trace()

        with self.assertNumQueries(1):
            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=trace.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["reference"], trace.reference)
        self.assertEqual(response.data["endpoint"], trace.endpoint.reference)
        self.assertIn("authentication", response.data)
        self.assertEqual(response.data["method"], trace.method)
        self.assertEqual(response.data["url"], trace.url)
        self.assertIn("started_at", response.data)
        self.assertIn("completed_at", response.data)
        self.assertIn("headers", response.data)
        self.assertIn("payload", response.data)
        self.assertIn("status_type", response.data)

    def test_cannot_retrieve_unknown_trace(self) -> None:
        with self.assertNumQueries(1):
            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=str(uuid.uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_trace_status_type_field(self) -> None:
        trace_info = [
            (100, "INFORMATIONAL"),
            (200, "SUCCESS"),
            (301, "REDIRECT"),
            (404, "CLIENT_ERROR"),
            (500, "SERVER_ERROR"),
            (None, None),
        ]

        for status_code, expected_status_type in trace_info:
            trace = get_trace(status_code=status_code)

            request = self.factory.get(detail_url)
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=trace.pk)

            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            self.assertEqual(response.data["status_type"], expected_status_type)

    def cannot_create_trace(self) -> None:
        with self.assertNumQueries(0):
            request = self.factory.post(list_url, {}, format="json")
            force_authenticate(request, user=self.user)
            response = list_view(request)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def cannot_update_trace(self) -> None:
        trace = get_trace()

        with self.assertNumQueries(0):
            request = self.factory.patch(list_url, {}, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=trace.pk)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def cannot_partial_update(self) -> None:
        trace = get_trace()

        with self.assertNumQueries(0):
            request = self.factory.put(detail_url, {}, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=trace.pk)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def cannot_delete(self) -> None:
        trace = get_trace()

        with self.assertNumQueries(0):
            request = self.factory.delete(detail_url, {}, format="json")
            force_authenticate(request, user=self.user)
            response = detail_view(request, pk=trace.pk)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

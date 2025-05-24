# pylint: disable=missing-function-docstring

from django.urls import reverse
from rest_framework import status

from compyle.lib.test import BaseAdminTest
from compyle.proxy import admin, models
from compyle.proxy.tests.factories import get_endpoint, get_trace

trace_admin_changelist_url = reverse("admin:proxy_trace_changelist")
trace_admin_change_url = lambda pk: reverse("admin:proxy_trace_change", args=(pk,))  # noqa: E731
trace_admin_add_url = reverse("admin:proxy_trace_add")


class TraceAdminTest(BaseAdminTest):
    """Test the admin for the :model:`compyle.proxy.models.Trace`."""

    def setUp(self) -> None:  # pylint: disable=invalid-name
        super().setUp()

        self.trace_admin = admin.TraceAdmin(models.Trace, self.site)
        self.change_read_only_fields = set(self.trace_admin.list_display)
        self.list_filter_fields = {
            "started_at",
            "completed_at",
        }

    def test_cannot_add_trace(self) -> None:
        self.assertFalse(self.trace_admin.has_add_permission(None))

    def test_cannot_update_trace(self) -> None:
        self.assertFalse(self.trace_admin.has_change_permission(None))

    def test_cannot_delete_trace(self) -> None:
        self.assertFalse(self.trace_admin.has_delete_permission(None))

    def test_get_trace_readonly_fields(self):
        self.assertSetEqual(set(self.trace_admin.get_readonly_fields(None)), self.change_read_only_fields)

    def test_get_traces_filter_fields(self):
        self.assertSetEqual(set(self.trace_admin.get_list_filter(None)), self.list_filter_fields)

    def test_can_list_traces(self) -> None:
        traces = [get_trace() for _ in range(3)]

        response = self.client.get(trace_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), len(traces))

    def test_cannot_list_traces_as_non_staff_user(self) -> None:
        self.client.logout()
        response = self.client.get(trace_admin_changelist_url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

    def test_can_list_traces_search_by_reference(self) -> None:
        traces = [get_trace() for _ in range(3)]
        reference = traces[0].reference

        response = self.client.get(trace_admin_changelist_url, {"q": reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 1)
        self.assertEqual(response.context["cl"].result_list[0].reference, reference)

    def test_can_list_traces_search_by_partial_reference(self) -> None:
        traces = [get_trace() for _ in range(3)]
        response = self.client.get(trace_admin_changelist_url, {"q": "-trace-"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context["cl"].result_list), len(traces))

    def test_can_list_traces_search_by_endpoint_reference(self) -> None:
        endpoint = get_endpoint()
        traces = [get_trace(endpoint=endpoint), get_trace(endpoint=endpoint), get_trace()]

        response = self.client.get(trace_admin_changelist_url, {"q": endpoint.reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [trace.reference for trace in response.context["cl"].result_list],
            [trace.reference for trace in traces if trace.endpoint.reference == endpoint.reference],
        )

    def test_can_list_traces_search_by_endpoint_partial_reference(self) -> None:
        endpoint = get_endpoint()
        traces = [get_trace(endpoint=endpoint), get_trace(endpoint=endpoint), get_trace()]
        partial_reference = endpoint.reference[:-1]

        response = self.client.get(trace_admin_changelist_url, {"q": partial_reference})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [trace.reference for trace in response.context["cl"].result_list],
            [trace.reference for trace in traces if partial_reference in trace.endpoint.reference],
        )

    def test_can_list_traces_search_by_endpoint_name(self) -> None:
        endpoint = get_endpoint()
        traces = [get_trace(endpoint=endpoint), get_trace(endpoint=endpoint), get_trace()]

        response = self.client.get(trace_admin_changelist_url, {"q": endpoint.name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [trace.reference for trace in response.context["cl"].result_list],
            [trace.reference for trace in traces if trace.endpoint.name == endpoint.name],
        )

    def test_can_list_traces_search_by_endpoint_partial_name(self) -> None:
        endpoint = get_endpoint(name="Youtube v1")
        traces = [get_trace(endpoint=endpoint), get_trace(endpoint=endpoint), get_trace()]
        partial_name = "tube"

        response = self.client.get(trace_admin_changelist_url, {"q": partial_name})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertEqual(len(response.context["cl"].result_list), 2)
        self.assertCountEqual(
            [trace.reference for trace in response.context["cl"].result_list],
            [trace.reference for trace in traces if partial_name in trace.endpoint.name],
        )

    def test_can_consult_trace(self) -> None:
        trace = get_trace()

        response = self.client.get(trace_admin_change_url(trace.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.reason_phrase)
        self.assertContains(response, trace.pk)

    def test_cannot_consult_trace_as_non_staff_user(self) -> None:
        trace = get_trace()

        self.client.logout()
        response = self.client.get(trace_admin_change_url(trace.pk))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND, response.reason_phrase)
        self.assertIn("/admin/login/", response.url)

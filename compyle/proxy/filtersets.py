from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter, FilterSet

from compyle.lib.filters import CharInFilter
from compyle.lib.filtersets import CreateUpdateFilterSet
from compyle.proxy import models


class ServiceFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.proxy.models.Service`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
    )
    endpoints = CharInFilter(
        label=_("endpoint references"),
        help_text=_("Filter by endpoint references. Multiple values allowed separated by comma."),
        field_name="endpoint__reference",
    )


class EndpointFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.proxy.models.Endpoint`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
    )
    traces = CharInFilter(
        label=_("traces"),
        help_text=_("Filter by trace reference. Multiple values allowed separated by comma."),
        field_name="endpoint_traces__endpoint",
    )


class TraceFilterSet(FilterSet):
    """Filterset for :class:`compyle.proxy.models.Trace`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
    )
    endpoints = CharInFilter(
        label=_("endpoint references"),
        help_text=_("Filter by endpoint references. Multiple values allowed separated by comma."),
        field_name="endpoint__reference",
    )
    services = CharInFilter(
        label=_("service references"),
        field_name="endpoint__service__reference",
        help_text=_("Filter by references of the related service (via endpoint)."),
    )
    status_code = CharInFilter(
        label=_("status codes"),
        help_text=_("Filter by status codes. Multiple values allowed separated by comma."),
        field_name="status_code",
    )
    status_code_startswith = CharFilter(
        label=_("status code starts with"),
        help_text=_("Filter by status code prefix (e.g. '2' for all 2xx)."),
        method="filter_status_prefix",
    )

    # pylint: disable=unused-argument
    def filter_status_prefix(self, queryset: QuerySet[models.Trace], name: str, value: str) -> QuerySet[models.Trace]:
        """Filters the queryset to include only traces whose status code starts with the given prefix.

        Args:
            queryset: The base queryset of Trace objects.
            name: The name of the filter field (ignored here).
            value: The prefix to match status codes against.

        Returns:
            A filtered queryset containing only matching Trace objects.
        """
        return queryset.filter(status_code__startswith=value)


class AuthenticationFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.proxy.models.Authentication`."""

    references = CharInFilter(
        label=_("references"),
        field_name="reference",
        help_text=_("Filter by authentication reference."),
    )
    has_access_token = BooleanFilter(
        label=_("has access token"),
        field_name="access_token",
        lookup_expr="isnull",
        help_text=_("True if access token is null, otherwize False."),
        exclude=True,
    )

from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet

from compyle.lib.filters import CharInFilter
from compyle.lib.filtersets import CreateUpdateFilterSet

# TODO fetch
# from unyc.django.utils.filtersets import CreateUpdateFilterSet
# https://git.spikeelabs.fr/spk/code/unyc/distributor/distributor-app/-/blob/main/event_broker/traceability/filtersets.py?ref_type=heads


    
class ServiceFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.proxy.models.Service`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
    )


class EndpointFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.proxy.models.Endpoint`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
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
    status_code = CharInFilter(
        label=_("status codes"),
        help_text=_("Filter by status codes. Multiple values allowed separated by comma."),
        field_name="status_code",
    )

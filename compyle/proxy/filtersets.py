from django.utils.translation import gettext_lazy as _

# TODO fetch
# from unyc.django.utils.filters import CharInFilter
# from unyc.django.utils.filtersets import CreateUpdateFilterSet
# https://git.spikeelabs.fr/spk/code/unyc/distributor/distributor-app/-/blob/main/event_broker/traceability/filtersets.py?ref_type=heads


class ServiceFilterSet:
    """Filterset for :class:`compyle.proxy.models.Service`."""

    pass


class EndpointFilterSet:
    """Filterset for :class:`compyle.proxy.models.Endpoint`."""

    pass


class TraceFilterSet:
    """Filterset for :class:`compyle.proxy.models.Trace`."""

    pass


#     class TraceFilterSet(CreateUpdateFilterSet):
#     """Filterset for :class:`event_broker.traceability.models.Trace`."""

#     references = CharInFilter(
#         label=_("references"),
#         field_name="reference",
#         help_text=_("Filter by references. Multiple values allowed separated by comma."),
#     )
#     publishers = CharInFilter(
#         label=_("publisher references"),
#         field_name="message__publisher__reference",
#         help_text=_("Filter by external references. Multiple values allowed separated by comma."),
#     )
#     listeners = CharInFilter(
#         label=_("listener references"),
#         field_name="listener__reference",
#         help_text=_("Filter by tenant references. Multiple values allowed separated by comma."),
#     )
#     messages = CharInFilter(
#         label=_("message references"),
#         field_name="message__reference",
#         help_text=_("Filter by message references. Multiple values allowed separated by comma."),
#     )
#     statuses = CharInFilter(
#         label=_("statuses"),
#         field_name="status",
#         help_text=_("Filter by statuses. Multiple values allowed separated by comma."),
#     )


# class TraceAttemptFilterSet(CreateUpdateFilterSet):
#     """Filterset for :class:`event_broker.traceability.models.TraceAttempt`."""

#     references = CharInFilter(
#         label=_("references"),
#         field_name="reference",
#         help_text=_("Filter by references. Multiple values allowed separated by comma."),
#     )
#     traces = CharInFilter(
#         label=_("trace references"),
#         field_name="trace__reference",
#         help_text=_("Filter by trace references. Multiple values allowed separated by comma."),
#     )
#     statuses = CharInFilter(
#         label=_("statuses"),
#         field_name="status",
#         help_text=_("Filter by statuses. Multiple values allowed separated by comma."),
#     )
#     http_codes = CharInFilter(
#         label=_("HTTP codes"),
#         field_name="http_code",
#         help_text=_("Filter by HTTP codes. Multiple values allowed separated by comma."),
#     )

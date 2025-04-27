from compyle.lib.admin import ReadOnlyAdminMixin
from compyle.proxy import models
from django.http import HttpRequest
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.decorators import register
from django.contrib.admin import ModelAdmin
from unyc.django.utils.admin import linkify # TODO

@register(models.Service)
class MessageAdmin(ModelAdmin[models.Service]):
    """Admin for :class:`compyle.proxy.models.Service`."""

    list_display = [
        "reference",
        "name",
        "trailing_slash",
        "auth_flow",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "reference",
        "created_at",
        "updated_at",
    ]

    search_fields = ["reference", "name"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["-updated_at",]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "name",
                    "trailing_slash",
                    "auth_flow",
                    "endpoints",
                )
            },
        ),
        (
            _("Technical info"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Service]:
        """Return the queryset with the prefetch of the endpoints.

        Args:
            request: The request instance.

        Returns:
            The queryset with the annotations.
        """
        return super().get_queryset(request).prefetch_related("endpoints")

# https://git.spikeelabs.fr/spk/code/unyc/distributor/distributor-app/-/blob/main/event_broker/traceability/admin.py?ref_type=heads

@register(models.Endpoint)
class EndpointAdmin(ModelAdmin[models.Endpoint]):
    """Admin for :class:`compyle.proxy.models.Endpoint`."""

    list_display = [
        "reference",
        "name",
        linkify("service"),
        
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "reference",
        "created_at",
        "updated_at",
    ]

    search_fields = ["reference", "name"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["-updated_at",]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "name",
                    "service",
                    "method",
                    "url",
                    "trailing_slash",
                    "auth_flow",
                )
            },
        ),
        (
            _("Technical info"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    ]


@register(models.Trace)
class TraceAdmin(ModelAdmin[models.Trace], ReadOnlyAdminMixin):
    """Admin for :class:`compyle.proxy.models.Trace`."""

    list_display = [
        "reference",
        "endpoint",
        "request_method",
        "request_url",
        "response_status_code",
        "created_at",
    ]
    readonly_fields = [
        "reference",
        "created_at",
    ]

    search_fields = ["reference", "endpoint__name"]
    list_filter = ["created_at"]
    ordering = ["-created_at",]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "endpoint",
                    "request_method",
                    "request_url",
                    "request_headers",
                    "request_body",
                    "response_status_code",
                    "response_headers",
                    "response_body",
                )
            },
        ),
        (
            _("Technical info"),
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    ]
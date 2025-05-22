from django.contrib import admin

from compyle.lib.inlines import ReadOnlyTabularInline
from compyle.proxy import models


class EndpointInline(admin.TabularInline):
    """Inline for :class:`compyle.proxy.models.Endpoint`."""

    show_change_link = True
    model = models.Endpoint
    fields = [
        "reference",
        "name",
        "method",
        "base_url",
        "slug",
        "response_type",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "reference",
        "created_at",
        "updated_at",
    ]
    extra = 0
    ordering = ["-created_at"]


class EndpointTraceInline(ReadOnlyTabularInline):
    """Inline for :class:`compyle.proxy.models.Trace` in the endpoint admin."""

    show_change_link = True
    model = models.Trace
    fields = [
        "reference",
        "started_at",
        "completed_at",
        "status_code",
    ]
    readonly_fields = fields
    ordering = ["-started_at"]


class AuthenticationTraceInline(ReadOnlyTabularInline):
    """Inline for :class:`compyle.proxy.models.Trace` in the authentication admin."""

    show_change_link = True
    model = models.Trace
    fields = [
        "reference",
        "endpoint",
        "started_at",
        "completed_at",
        "status_code",
    ]
    readonly_fields = fields
    ordering = ["-started_at"]

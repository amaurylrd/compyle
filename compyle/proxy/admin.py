from admin_action_tools import ActionFormMixin, add_form_to_action
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_object_actions import DjangoObjectActions, action

from compyle.lib.admin import BaseCreateUpdateModelAdmin, ReadOnlyAdminMixin, linkify
from compyle.proxy import forms, inlines, models
from compyle.proxy.tasks import async_request


@register(models.Service)
class ServiceAdmin(BaseCreateUpdateModelAdmin):
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
    ordering = ["-updated_at"]

    inlines = [inlines.EndpointInline]  # type: ignore[assignment]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "name",
                    "trailing_slash",
                    "auth_flow",
                )
            },
        ),
        (
            _("Technical info"),
            {
                "classes": ("technical-info",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "description": _("These fields are automatically managed."),
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


@register(models.Endpoint)
class EndpointAdmin(ActionFormMixin, DjangoObjectActions, BaseCreateUpdateModelAdmin):
    """Admin for :class:`compyle.proxy.models.Endpoint`."""

    list_display = [
        "reference",
        "name",
        linkify("service"),
        "method",
        "base_url",
        "slug",
        "response_type",
        "created_at",
        "updated_at",
    ]  # TODO auth_method
    readonly_fields = [
        "reference",
        "created_at",
        "updated_at",
    ]

    search_fields = ["reference", "name", "service__reference", "service__name"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "name",
                    "service",
                    "method",
                    "base_url",
                    "slug",
                    "response_type",
                )
            },
        ),
        (
            _("Technical info"),
            {
                "classes": ("technical-info",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "description": _("These fields are automatically managed."),
            },
        ),
    ]
    inlines = [inlines.TraceInline]  # type: ignore[assignment]

    change_actions = ["request"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Endpoint]:
        """Return the queryset with the prefetch of the endpoints.

        Args:
            request: The request instance.

        Returns:
            The queryset with the annotations.
        """
        return super().get_queryset(request).select_related("service").prefetch_related("endpoint_traces")

    # pylint: disable=unused-argument
    @add_form_to_action(forms.TraceForm, display_queryset=False)
    @action(label=_("Request"), description=_("Request this endpoint"))
    def request(self, request: HttpRequest, obj: models.Endpoint, form: forms.TraceForm) -> None:
        """Action to request the endpoint with the given parameters.

        Args:
            request: The request object.
            obj: The endpoint object.
            form: The form with the parameters.
        """
        try:
            task = async_request.delay(
                obj.reference,
                form.cleaned_data.get("authentication"),
                form.cleaned_data.get("params"),
                form.cleaned_data.get("headers"),
                form.cleaned_data.get("payload"),
            )

            self.message_user(
                request,
                _("The endpoint has been successfully requested: task {task_id}.").format(task_id=task.id),
                messages.SUCCESS,
            )
        except Exception as exception:
            self.message_user(
                request,
                _("An error occurred while requesting the endpoint: {error}.").format(error=str(exception)),
                messages.ERROR,
            )


@register(models.Trace)
class TraceAdmin(ModelAdmin, ReadOnlyAdminMixin):
    """Admin for :class:`compyle.proxy.models.Trace`."""

    list_display = [
        "reference",
        linkify("endpoint"),
        "method",
        "url",
        "status_code",
        "started_at",
        "completed_at",
    ]
    readonly_fields = list_display

    search_fields = ["reference", "endpoint__name", "endpoint__reference"]
    list_filter = ["started_at", "completed_at"]
    ordering = ["-started_at"]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "endpoint",
                    "method",
                    "url",
                    "started_at",
                    "completed_at",
                    "status_code",
                    "params",
                    "headers",
                    "payload",
                )
            },
        ),
        # (
        #     _("Technical info"),
        #     {
        #         "classes": ("technical-info",),
        #         "fields": (
        #             "request_method",
        #             "request_url",
        #             "request_headers",
        #             "request_body",
        #             "response_headers",
        #             "response_body",
        #         ),
        #         "description": _("These fields are automatically managed."),
        #     },
        # ),
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Trace]:
        """Return the queryset with the related endpoint.

        Args:
            request: The request instance.

        Returns:
            The queryset with the annotations.
        """
        return super().get_queryset(request).select_related("endpoint", "authentication")

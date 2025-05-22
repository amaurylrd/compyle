from admin_action_tools import ActionFormMixin, add_form_to_action
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_object_actions import DjangoObjectActions, action

from compyle.lib.admin import BaseCreateUpdateModelAdmin, ReadOnlyAdminMixin, linkify
from compyle.proxy import choices, forms, inlines, models
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
                    "token_url",
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
    inlines = [inlines.EndpointTraceInline]  # type: ignore[assignment]

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
                form.data.get("authentication"),
                form.cleaned_data.get("params"),
                form.cleaned_data.get("headers"),
                form.cleaned_data.get("payload"),
                timeout=60,
            )

            self.message_user(
                request,
                _("The endpoint has been successfully requested: task {task_id}.").format(task_id=task.id),
                messages.SUCCESS,
            )
        except Exception as exception:  # pylint: disable=broad-except
            self.message_user(
                request,
                _("An error occurred while requesting the endpoint: {error}.").format(error=str(exception)),
                messages.ERROR,
            )


@register(models.Trace)
class TraceAdmin(ReadOnlyAdminMixin, ModelAdmin):
    """Admin for :class:`compyle.proxy.models.Trace`."""

    list_display = [
        "reference",
        linkify("endpoint"),
        linkify("authentication"),
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


@register(models.Authentication)
class AuthenticationAdmin(BaseCreateUpdateModelAdmin):
    """Admin for :class:`compyle.proxy.models.Authentication`."""

    list_display = [
        "reference",
        "email",
        "is_token_valid",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "reference",
        "is_token_valid",
        "created_at",
        "updated_at",
    ]
    # todo faire un truc pour le many2many ici
    search_fields = ["reference", "auth_traces__endpoint__reference"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "email",
                )
            },
        ),
        (
            choices.AuthFlow.API_KEY.label,
            {
                "fields": ("api_key",),
            },
        ),
        (
            choices.AuthFlow.BASIC_AUTHENTICATION.label,
            {
                "fields": (
                    "login",
                    "password",
                ),
            },
        ),
        (
            _("OAuth2"),
            {
                "fields": (
                    "client_id",
                    "client_secret",
                    "access_token",
                    "expires_at",
                    "refresh_token",
                    "is_token_valid",
                ),
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
    inlines = [inlines.AuthenticationTraceInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Authentication]:
        """Return the queryset with the related entities prefetched.

        Args:
            request: The request instance.

        Returns:
            The queryset with the annotations.
        """
        return super().get_queryset(request).prefetch_related("auth_traces", "auth_traces__endpoint")

    def is_token_valid(self, obj: models.Authentication) -> bool:  # pragma: no cover
        """Retrieve the property 'is_token_valid" to be displayed as on and off indicator instead of default string.

        Args:
            The object instance.

        Returns:
            The boolean value.
        """
        return obj.is_token_valid

    is_token_valid.boolean = True  # type: ignore[attr-defined]

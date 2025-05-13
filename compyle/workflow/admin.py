from admin_action_tools import ActionFormMixin, add_form_to_action
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_object_actions import DjangoObjectActions, action

from compyle.lib.admin import BaseCreateUpdateModelAdmin, ReadOnlyAdminMixin, linkify
from compyle.workflow import inlines, models


@register(models.Workflow)
class WorkflowAdmin(ActionFormMixin, DjangoObjectActions, BaseCreateUpdateModelAdmin):
    """Admin for :class:`compyle.workflow.models.Workflow`."""

    list_display = [
        "reference",
        "name",
        "description",
        "active",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "reference",
        "created_at",
        "updated_at",
    ]

    search_fields = ["reference", "name"]
    list_filter = ["active", "created_at", "updated_at"]
    ordering = ["active", "-updated_at"]

    inlines = [inlines.WorkflowStepInline]  # type: ignore[assignment]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "name",
                    "description",
                    "active",
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
    change_actions = ["run"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Workflow]:
        """Return the queryset with the prefetch of the workflow steps.

        Args:
            request: The request instance.

        Returns:
            The queryset with the annotations.
        """
        return super().get_queryset(request).prefetch_related("steps")

    # pylint: disable=unused-argument
    @action(label=_("Run"), description=_("Run this workflow"))
    def run(self, request: HttpRequest, obj: models.Workflow, form) -> None:
        """Action to request the endpoint with the given parameters.

        Args:
            request: The request object.
            obj: The endpoint object.
            form: The form with the parameters.
        """
        pass


@register(models.WorkflowStep)
class WorkflowStepAdmin(BaseCreateUpdateModelAdmin):
    """Admin for :class:`compyle.workflow.models.WorkflowStep`."""

    list_display = [
        "reference",
        linkify("workflow"),
        "status",
        "trigger_type",
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

    # TODO inlines = [inlines.EndpointInline]  # type: ignore[assignment]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "reference",
                    "workflow",
                    "configuration",
                    "trigger_type",
                    "repeat_every",
                    "next_run_at",
                    "async_task",
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.WorkflowStep]:
        """Return the queryset with the prefetch of the workflow and the workflow steps that this step depends on.

        Args:
            request: The request instance.

        Returns:
            The queryset with the annotations.
        """
        return super().get_queryset(request).select_related("workflow").prefetch_related("depends_on")

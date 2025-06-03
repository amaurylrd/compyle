from django.contrib import admin
from django.db.models import Case, QuerySet, When
from django.http import HttpRequest

from compyle.workflow import models
from compyle.workflow.utils import topological_sort


class WorkflowStepInline(admin.TabularInline):
    """Inline for :class:`compyle.workflow.models.WorkflowStep`."""

    show_change_link = True
    model = models.WorkflowStep
    fields = [
        "reference",
        "status",
        # "method",
        # "base_url",
        # "slug",
        # "response_type",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "reference",
        "created_at",
        "updated_at",
    ]
    extra = 0
    # ordering = ["-created_at"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.WorkflowStep]:
        """This method is overridden to sort the steps in topological order based on their dependencies.

        Args:
            request: The request instance.

        Returns:
            The sorted queryset of WorkflowStep instances.
        """
        queryset = super().get_queryset(request).prefetch_related("depends_on")
        sorted_steps = topological_sort(queryset)

        order = Case(*[When(pk=step.pk, then=pos) for pos, step in enumerate(sorted_steps)])

        return queryset.order_by(order)

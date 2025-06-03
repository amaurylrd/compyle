from django.utils.translation import gettext_lazy as _

from compyle.lib.filters import CharInFilter
from compyle.lib.filtersets import CreateUpdateFilterSet


class WorkflowFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.workflow.models.Workflow`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
    )


class WorkflowStepFilterSet(CreateUpdateFilterSet):
    """Filterset for :class:`compyle.workflow.models.WorkflowStep`."""

    references = CharInFilter(
        label=_("references"),
        help_text=_("Filter by references. Multiple values allowed separated by comma."),
        field_name="reference",
    )

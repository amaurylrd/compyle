from django.db import models
from django.utils.translation import gettext_lazy as _

from compyle.lib.models import BaseModel
from compyle.proxy.choices_workflow import StepStatus, StepTriggerType


class Workflow(BaseModel):
    """This model represents a which is a container of ordered steps."""

    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("The endpoint name, for a more human display."),
        max_length=255,
        unique=True,
    )
    description = models.TextField(
        verbose_name=_("description"),
        help_text=_("The description of the workflow."),
        default=None,
        null=True,
        blank=True,
    )
    active = models.BooleanField(
        verbose_name=_("active"),
        help_text=_("Tells if the workflow is active."),
        default=True,
        blank=True,
    )

    steps: models.QuerySet["WorkflowStep"]

    class Meta:
        verbose_name = _("workflow")
        verbose_name_plural = _("workflows")

    def __str__(self) -> str:
        return self.name


class WorkflowStep(BaseModel):
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        help_text=_("The order steps are executed in."),
        default=0,
    )
    status = models.CharField(
        verbose_name=_("status"),
        help_text=_("The status of the step."),
        choices=StepStatus.choices,
        default=StepStatus.PENDING,
        max_length=255,
    )
    configuration = models.JSONField(
        verbose_name=_("configuration"),
        help_text=_("The configuration for that task."),
        default=dict,
    )
    trigger_type = models.CharField(
        verbose_name=_("trigger type"),
        help_text=_("The status of the step."),
        choices=StepTriggerType.choices,
        default=StepTriggerType.MANUAL,
        max_length=255,
    )
    async_task = models.BooleanField(
        verbose_name=_("async"),
        help_text=_("Tells if this step runs asynchronously."),
        default=False,
        blank=True,
    )

    workflow = models.ForeignKey(
        verbose_name=_("archived by"),
        help_text=_("The workflow of the step."),
        to=Workflow,
        related_name="steps",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("workflow step")
        verbose_name_plural = _("workflow steps")
        ordering = ["order"]


class WorkflowStepTask:
    pass


# class WorkflowExecution:
#     pass
# started_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)

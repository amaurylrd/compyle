from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from compyle.lib.models import BaseModel, CreateUpdateMixin
from compyle.workflow.choices import StepStatus, StepTriggerType


class Workflow(BaseModel, CreateUpdateMixin):
    """This model represents a Directed Acyclic Graph (DAG) style workflow execution."""

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

    def get_dependency_graph(self) -> dict[str, list[str]]:
        return {step.reference: [dep.reference for dep in step.depends_on.all()] for step in self.steps.all()}


class WorkflowStep(BaseModel, CreateUpdateMixin):
    # allows parallel execution, async triggers, and conditional flows.

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
        blank=True,
    )
    trigger_type = models.CharField(
        verbose_name=_("trigger type"),
        help_text=_("The status of the step."),
        choices=StepTriggerType.choices,
        default=StepTriggerType.MANUAL,
        max_length=255,
    )
    repeat_every = models.DurationField(
        verbose_name=_("repeat every"),
        help_text=_("How often to repeat the workflow."),
        null=True,
        blank=True,
        default=timedelta(days=2),
    )
    next_run_at = models.DateTimeField(
        verbose_name=_("next run"),
        help_text=_("Next scheduled execution time."),
        null=True,
        blank=True,
    )
    async_task = models.BooleanField(
        verbose_name=_("async"),
        help_text=_("Tells if this step runs asynchronously."),
        default=False,
        blank=True,
    )

    workflow = models.ForeignKey(
        verbose_name=_("workflow"),
        help_text=_("The workflow of the step."),
        to=Workflow,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    depends_on = models.ManyToManyField(
        verbose_name=_("depends on"),
        help_text=_("Steps that must complete before this one starts."),
        to="self",
        symmetrical=False,
        related_name="unblocks",
        blank=True,
    )

    class Meta:
        verbose_name = _("workflow step")
        verbose_name_plural = _("workflow steps")
        # ordering = ["order"]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["workflow", "order"],
        #         name="unique_order_per_workflow",
        #     )
        # ]

    @property
    @admin.display(description=_("pending steps"))
    def pending_steps(self) -> models.QuerySet["WorkflowStep"]:
        """Return a queryset of WorkflowStep instances that depend on this step and are currently in the PENDING status.

        Returns:
            These are the steps that cannot start until this step completes.
        """
        return self.unblocks.filter(status=StepStatus.PENDING)

    @property
    @admin.display(description=_("is ready"), boolean=True)
    def is_ready(self) -> bool:
        """Check if the workflow step is ready to be executed.

        Returns:
            bool: True if the step can be safely executed, False otherwise.
        """
        return self.status == StepStatus.PENDING and all(
            step.status == StepStatus.SUCCESS for step in self.depends_on.all()
        )

    @property
    @admin.display(description=_("is scheduled"), boolean=True)
    def is_scheduled(self) -> bool:
        """Check whether the workflow step is scheduled.

        Returns:
            True if the workflow step has scheduled datetime in the future, False otherwise.
        """
        return self.next_run_at and timezone.now() < self.next_run_at

    def reschedule(self) -> None:
        if self.repeat_every:
            self.next_run_at = timezone.now() + self.repeat_every
            self.save()

            # start_repeating_workflow.apply_async(
            #     args=[workflow.id],
            #     eta=workflow.next_run_at
            # )


class WorkflowTask(BaseModel):
    task_id = models.CharField(
        verbose_name=_("task_id"),
        help_text=_("Celery task ID for tracking execution."),
        max_length=255,
        null=True,
        blank=True,
    )
    result = models.JSONField(
        verbose_name=_("result"),
        help_text=_("Result of the task."),
        default=dict,
        blank=True,
    )
    started_at = models.DateTimeField(
        verbose_name=_("started at"),
        help_text=_("The datetime of the task execution."),
        auto_now_add=True,
    )
    completed_at = models.DateTimeField(
        verbose_name=_("completed at"),
        help_text=_("The datetime of the task completion."),
        default=None,
        null=True,
        blank=True,
    )

    step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("step"),
        help_text=_("The workflow step this task belongs to."),
    )

    class Meta:
        verbose_name = _("workflow task")
        verbose_name_plural = _("workflow tasks")


# class WorkflowExecution:
#     pass
# started_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)

# class WorkflowExecution(BaseModel):
#     workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="executions")
#     started_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=ExecutionStatus.choices, default=ExecutionStatus.PENDING)

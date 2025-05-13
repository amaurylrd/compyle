from django.db.models import TextChoices
from django.utils.translation import pgettext_lazy


class StepStatus(TextChoices):
    PENDING = "pending", pgettext_lazy("workflow step status", "Pending")
    RUNNING = "running", pgettext_lazy("workflow step status", "Running")
    RETRYING = "retrying", pgettext_lazy("workflow step status", "Retrying")
    SUCCESS = "success", pgettext_lazy("workflow step status", "Success")
    FAILED = "failed", pgettext_lazy("workflow step status", "Failed")


class StepTriggerType(TextChoices):
    MANUAL = "manual", pgettext_lazy("workflow step trigger type", "Manual by user")
    AUTO = "auto", pgettext_lazy("workflow step trigger type", "Automatically after previous step completes")
    SCHEDULED = "scheduled", pgettext_lazy("workflow step trigger type", "Scheduled at a specific time or interval")

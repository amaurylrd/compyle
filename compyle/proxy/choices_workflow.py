from django.db.models import TextChoices
from django.utils.translation import pgettext_lazy


class StepStatus(TextChoices):
    PENDING = "pending", pgettext_lazy("task status", "Pending")
    RUNNING = "running", pgettext_lazy("task status", "Running")
    RETRYING = "retrying", pgettext_lazy("trask status", "Retrying")
    SUCCESS = "success", pgettext_lazy("trask status", "Success")
    FAILED = "failed", pgettext_lazy("trask status", "Failed")


class StepTriggerType(TextChoices):
    MANUAL = "manual", pgettext_lazy("trigger type", "Manual by user")
    AUTO = "auto", pgettext_lazy("trigger type", "Automatically after previous step completes")
    SCHEDULED = "scheduled", pgettext_lazy("trigger type", "Scheduled at a specific time or interval")

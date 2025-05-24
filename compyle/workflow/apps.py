from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkflowConfig(AppConfig):
    """Configuration for the workflow app."""

    name = "compyle.workflow"
    verbose_name = _("workflow")
    verbose_name_plural = _("workflows")

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class CreateUpdateMixin:
    """A mixin class that provides automatic tracking of creation and update timestamps."""

    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        help_text=_("The datetime of the creation."),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated at"),
        help_text=_("The datetime of the last update."),
        auto_now=True,
    )


class BaseModel(CreateUpdateMixin, models.Model):
    """A base model class that extends CreateUpdateMixin and provides a reference field as pk."""

    reference = models.CharField(
        verbose_name=_("reference"),
        help_text=_("The entity reference."),
        max_length=255,
        default=uuid.uuid4,
        primary_key=True,
    )

    class Meta:
        abstract = True
        ordering = ["updated_at"]

from django.contrib import admin
from django.db import models
from django.http import HttpRequest


class ReadOnlyTabularInline(admin.TabularInline):
    """An inline to disable deletion and modification."""

    extra = 0
    can_delete = False

    # pylint: disable=unused-argument
    def has_add_permission(self, request: HttpRequest, obj: models.Model | None = None) -> False:
        """Override the 'has_add_permission' method to disable the add button."""
        return False

    # pylint: disable=unused-argument
    def has_change_permission(self, request: HttpRequest, obj: models.Model | None = None) -> False:
        """Override the 'has_change_permission' method to disable the change action."""
        return False

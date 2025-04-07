from django.contrib.admin import ModelAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import capfirst


class ReadOnlyAdminMixin:
    """Read-only inline mixin, disable create, edit, and delete permissions on inline."""

    @property
    def readonly_fields(self):
        """Build and return list of readonly_fields."""
        readonly_fields = list(
            set(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )
        )

        return readonly_fields

    def has_add_permission(self, request, obj=None) -> False:  # pylint: disable=unused-argument
        """Prevent user to add."""
        return False

    def has_change_permission(self, request, obj=None) -> False:  # pylint: disable=unused-argument
        """Prevent user to change."""
        return False

    def has_delete_permission(self, request, obj=None) -> False:  # pylint: disable=unused-argument
        """Prevent user to remove."""
        return False


def linkify(field_name: str) -> callable:
    """Returns a function that links to the related object's admin change page.

    Args:
        field_name: The name of the relation field to linkify.

    Returns:
        A function that takes an object and returns a link to the related object's admin change page.
    """

    def _linkify(obj) -> str:
        related_obj = getattr(obj, field_name)

        if related_obj is None:
            return "—"

        app_label = related_obj._meta.app_label  # pylint: disable=protected-access
        model_name = related_obj._meta.model_name  # pylint: disable=protected-access
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[related_obj.pk])

        return format_html('<a href="{}">{}</a>', url, capfirst(str(related_obj)))

    _linkify.admin_order_field = field_name
    _linkify.short_description = capfirst(field_name.replace("_", " "))

    return _linkify


class BaseCreateUpdateModelAdmin(ModelAdmin):
    class Media:
        css = {"all": ("css/admin.css",)}

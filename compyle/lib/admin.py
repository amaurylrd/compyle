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

    def has_add_permission(self, request, obj=None) -> bool:  # pylint: disable=W0613
        """Prevent user to add."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # pylint: disable=W0613
        """Prevent user to change."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # pylint: disable=W0613
        """Prevent user to remove."""
        return False

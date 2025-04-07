from django_filters import FilterSet, DateTimeFilter
from django.utils.translation import gettext_lazy as _

class CreateUpdateFilterSet(FilterSet):
    """Base filterset to add created/updated filters to model that inherits from the CreateUpdateMixin."""

    created_after = DateTimeFilter(
        label=_("Created after"),
        help_text=_("Filter by items created after this datetime."),
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = DateTimeFilter(
        label=_("Created before"),
        help_text=_("Filter by items created before this datetime."),
        field_name="created_at",
        lookup_expr="lte",
    )
    updated_after = DateTimeFilter(
        label=_("Updated after"),
        help_text=_("Filter by items updated after this datetime."),
        field_name="updated_at",
        lookup_expr="gte",
    )
    updated_before = DateTimeFilter(
        label=_("Updated before"),
        help_text=_("Filter by items updated before this datetime."),
        field_name="updated_at",
        lookup_expr="lte",
    )

    class Meta:
        abstract = True

from django_filters import filters


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    """A filter that allows for a list of strings to be passed in as a filter."""

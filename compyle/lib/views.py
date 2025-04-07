from typing import Any

from rest_framework import serializers, viewsets


class BaseModelViewSet(viewsets.ModelViewSet[Any]):
    """Base class for all read-only model viewsets in the compyle Django app."""

    serializer_classes: dict[str, type[serializers.BaseSerializer[Any]]] = {}

    def get_serializer_class(self) -> type[serializers.BaseSerializer[Any]]:
        """Return the serializer class from the dict `serializer_classes` that should be used for the request.

        Returns:
            The serializer class that should be used for the request.
        """
        return self.serializer_classes.get(self.action, super().get_serializer_class())

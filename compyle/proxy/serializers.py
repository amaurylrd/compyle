from rest_framework import serializers

from compyle.proxy import models

# TODO retrieve CreateUpdateSerializerMixin


class ServiceSerializer(serializers.ModelSerializer[models.Service]):
    # TODO
    class Meta:
        model = models.Service
        fields = [
            "reference",
            "name",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class EndpointSerializer(serializers.ModelSerializer[models.Endpoint]):
    # TODO
    class Meta:
        model = models.Endpoint
        fields = [
            "reference",
            "name",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class TraceSerializer(serializers.ModelSerializer[models.Trace]):
    """Serializer for :class:`event_broker.traceability.models.Trace`."""

    class Meta:
        model = models.Trace
        fields = [
            "reference",
            "endpoint",
            "status",
            "status_code",
            "status_type",
            "headers",
            "payload",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields

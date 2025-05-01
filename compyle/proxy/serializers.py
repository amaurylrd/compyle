from typing import Any

from django.db import transaction
from rest_framework import serializers, status

from compyle.proxy import models


class EndpointSerializer(serializers.ModelSerializer[models.Endpoint]):
    """Serializer for :class:`comprle.proxy.models.Endpoint`."""

    traces = serializers.PrimaryKeyRelatedField(
        source="endpoint_traces",
        many=True,
        read_only=True,
    )

    class Meta:
        model = models.Endpoint
        fields = [
            "reference",
            "name",
            "base_url",
            "slug",
            "method",
            "response_type",
            "auth_method",
            "service",
            "traces",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "reference",
            "created_at",
            "updated_at",
        ]


class ServiceSerializer(serializers.ModelSerializer[models.Service]):
    """Serializer for :class:`comprle.proxy.models.Service`."""

    endpoints = EndpointSerializer(many=True)

    class Meta:
        model = models.Service
        fields = [
            "reference",
            "name",
            "trailing_slash",
            "auth_flow",
            "endpoints",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "reference",
            "created_at",
            "updated_at",
        ]

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> models.Service:
        """Create a new service and its endpoints.

        Args:
            validated_data: The validated data for the service.

        Returns:
            The created service instance.
        """
        endpoints_data = validated_data.pop("endpoints", [])
        service = models.Service.objects.create(**validated_data)

        if endpoints_data:
            endpoints = [models.Endpoint(service=service, **endpoint_data) for endpoint_data in endpoints_data]
            models.Endpoint.objects.bulk_create(endpoints)

        return service

    @transaction.atomic
    def update(self, instance: models.Service, validated_data: dict[str, Any]) -> models.Service:
        """Update an existing service and its endpoints.

        Args:
            instance: The service instance to update.
            validated_data: The validated data for the service.

        Returns:
            The updated service instance.
        """
        endpoints_data = validated_data.pop("endpoints", [])

        instance = super().update(instance, validated_data)
        service_endpoints = instance.endpoints.all()

        if not endpoints_data:
            service_endpoints.delete()
        else:
            service_endpoints_ids = {e.reference: e for e in service_endpoints}

            update_endpoints = []
            create_endpoints = []

            for endpoint_data in endpoints_data:
                reference = endpoint_data.get("reference")

                if reference in service_endpoints:
                    endpoint = service_endpoints_ids.pop(reference)

                    endpoint_serializer = EndpointSerializer(instance=endpoint, data=endpoint_data, partial=True)
                    endpoint_serializer.is_valid(raise_exception=True)
                    endpoint = endpoint_serializer.save()

                    update_endpoints.append(endpoint)
                else:
                    endpoint = models.Endpoint(service=instance, **endpoint_data)

                    create_endpoints.append(endpoint)

            if update_endpoints:
                models.Endpoint.objects.bulk_update(update_endpoints, self.fields["endpoints"].child.Meta.fields)

            if create_endpoints:
                models.Endpoint.objects.bulk_create(create_endpoints)

            if service_endpoints_ids:
                models.Endpoint.objects.filter(reference__in=service_endpoints_ids).delete()

        return instance


class RequestSerializer(serializers.Serializer):
    """Serializer for request data."""

    authentication = serializers.PrimaryKeyRelatedField(
        queryset=models.Authentication.objects.all(),
        required=False,
        allow_null=True,
    )
    params = serializers.DictField(required=False, allow_null=True, allow_empty=True, default={})
    headers = serializers.DictField(required=False, allow_null=True, allow_empty=True, default={})
    body = serializers.DictField(required=False, allow_null=True, default=None)
    task_id = serializers.CharField(read_only=True)


class TraceSerializer(serializers.ModelSerializer[models.Trace]):
    """Serializer for :class:`event_broker.traceability.models.Trace`."""

    status_type = serializers.SerializerMethodField()

    class Meta:
        model = models.Trace
        fields = [
            "reference",
            "started_at",
            "completed_at",
            "method",
            "url",
            "status_code",
            "status_type",
            "headers",
            "payload",
            "params",
            "endpoint",
            "authentication",
        ]
        read_only_fields = fields

    def get_status_type(self, obj: models.Trace) -> str:
        """Get the status type of the trace based on its status code.

        Args:
            obj: The trace instance.

        Returns:
            The status type of the trace or None if not applicable.
        """
        if status.is_informational(obj.status_code):
            return "INFORMATIONAL"
        if status.is_success(obj.status_code):
            return "SUCCESS"
        if status.is_redirect(obj.status_code):
            return "REDIRECT"
        if status.is_client_error(obj.status_code):
            return "CLIENT_ERROR"
        if status.is_server_error(obj.status_code):
            return "SERVER_ERROR"
        return None

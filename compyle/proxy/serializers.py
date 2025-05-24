from typing import Any

from django.db import transaction
from rest_framework import serializers, status

from compyle.proxy import models


class EndpointSerializer(serializers.ModelSerializer[models.Endpoint]):
    """Serializer for :class:`compyle.proxy.models.Endpoint`."""

    service = serializers.PrimaryKeyRelatedField(
        queryset=models.Service.objects.all(),
    )
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self.context.get("nested", False):
            self.fields["service"].required = False


class ServiceSerializer(serializers.ModelSerializer[models.Service]):
    """Default serializer for :class:`compyle.proxy.models.Service`."""

    endpoints = EndpointSerializer(many=True, read_only=True)

    class Meta:
        model = models.Service
        fields = [
            "reference",
            "name",
            "trailing_slash",
            "auth_flow",
            "token_url",
            "endpoints",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "reference",
            "created_at",
            "updated_at",
        ]


class ServiceCreateSerializer(ServiceSerializer):
    """Serializer for :class:`compyle.proxy.models.Service` for create action."""

    endpoints = EndpointSerializer(many=True, required=False, context={"nested": True})

    class Meta:
        model = ServiceSerializer.Meta.model
        fields = ServiceSerializer.Meta.fields
        read_only_fields = ServiceSerializer.Meta.read_only_fields

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

        if "endpoints" in self.initial_data and endpoints_data:
            endpoints = [models.Endpoint(service=service, **endpoint_data) for endpoint_data in endpoints_data]
            models.Endpoint.objects.bulk_create(endpoints)

        return service


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
    timeout = serializers.FloatField(required=False, allow_null=True, default=None)
    task_id = serializers.CharField(read_only=True)


class TraceSerializer(serializers.ModelSerializer[models.Trace]):
    """Serializer for :class:`compyle.proxy.models.Trace`."""

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
        # TODO faire un choices ou juste passer en minnuscule les trucs ou juste le retirer
        if obj.status_code:
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


class AuthenticationSerializer(serializers.ModelSerializer[models.Authentication]):
    """Serializer for :class:`compyle.proxy.models.Authentication`."""

    class Meta:
        model = models.Authentication
        fields = [
            "reference",
            "email",
            "login",
            "password",
            "client_id",
            "client_secret",
            "api_key",
            "access_token",
            "expires_at",
            "refresh_token",
        ]
        read_only_fields = fields

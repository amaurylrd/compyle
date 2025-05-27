from typing import Any

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

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
            "documentation_url",
            "trailing_slash",
            "auth_flow",
            "token_url",
            "auth_url",
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


class AuthorizeSerialize(serializers.Serializer):
    """Serializer for authorize action."""

    authentication = serializers.PrimaryKeyRelatedField(
        queryset=models.Authentication.objects.all(),
    )
    redirect_uri = serializers.URLField(
        help_text=_("The URI to redirect to after authorization. Must match the registered URI."),
    )
    scopes = serializers.ListField(
        help_text=_("The list of OAuth2 scopes as URLs"),
        child=serializers.URLField(),
        required=False,
        default=list,
    )
    state = serializers.CharField(
        help_text=_("An opaque value used by the client to maintain state between the request and callback."),
        required=False,
        max_length=128,
    )
    login_hint = serializers.CharField(
        help_text=_("The email address of the user to log in."),
        required=False,
    )


class AuthorizationSerializer(serializers.Serializer):
    """Serializer for the authorize action response."""

    authorization_url = serializers.URLField()
    state = serializers.CharField()


class CallbackSerializer(serializers.Serializer):
    """Serializer for callback action."""

    code = serializers.CharField()
    state = serializers.CharField()


class RequestSerializer(serializers.Serializer):
    """Serializer for request action."""

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

    class Meta:
        model = models.Trace
        fields = [
            "reference",
            "started_at",
            "completed_at",
            "method",
            "url",
            "status_code",
            "status",
            "headers",
            "payload",
            "endpoint",
            "authentication",
        ]
        read_only_fields = fields


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
            "state",
            "authorization_code",
            "access_token",
            "expires_at",
            "refresh_token",
        ]
        read_only_fields = fields


class StatusCountSerializer(serializers.Serializer):
    """Serialier for status pie chart."""

    name = serializers.CharField()
    value = serializers.IntegerField()


class StatisticsSerializer(serializers.Serializer):
    """Serialier for statistics."""

    status_counter = StatusCountSerializer(many=True)

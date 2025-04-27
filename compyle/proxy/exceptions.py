from django.utils.translation import gettext_lazy as _
from drf_standardized_errors.openapi_serializers import ClientErrorEnum
from rest_framework import serializers, status
from rest_framework.exceptions import APIException


class RequestArchived(APIException):
    """API exception for when requesting an endpoint that is not active."""

    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_code = "endpoint_archived"
    default_detail = _("The endpoint is archived, the request cannot be triggered.")


class RequestPreconditionSerializer(serializers.Serializer):
    """Serializer for error for OpenAPI doc."""

    code = serializers.CharField()
    detail = serializers.CharField()
    attr = serializers.CharField(allow_null=True)


class RequestPreconditionResponseSerializer(serializers.Serializer):
    """Serializer for error response for OpenAPI doc."""

    type = serializers.ChoiceField(ClientErrorEnum.choices)
    errors = RequestPreconditionSerializer(many=True)

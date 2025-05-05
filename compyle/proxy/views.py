from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, response, status, viewsets
from rest_framework.decorators import action

from compyle.lib.views import BaseModelViewSet
from compyle.proxy import filtersets, models, serializers
from compyle.proxy.tasks import async_request


class ServiceViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Service`."""

    queryset = models.Service.objects.all().prefetch_related("endpoints")
    serializer_class = serializers.ServiceSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.ServiceFilterSet

    search_fields = ["reference", "name"]
    ordering_fields = ["reference", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[models.Service]:
        """Returns the queryset of `Service` objects with prefetch optimization for GET requests.

        Returns:
            The queryset of `Service` objects.
        """
        queryset = super().get_queryset()

        if self.request.method == "GET":
            queryset.prefetch_related(
                Prefetch(
                    "endpoints__endpoint_traces",
                    queryset=models.Trace.objects.only("pk", "endpoint"),
                )
            )

        return queryset


class EndpointViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Service`."""

    queryset = models.Endpoint.objects.all().select_related("service").prefetch_related("endpoint_traces")
    serializer_class = serializers.EndpointSerializer
    serializer_classes = {
        "request": serializers.RequestSerializer,
    }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.EndpointFilterSet

    search_fields = ["reference", "name", "service__reference"]
    ordering_fields = ["reference", "name", "created_at", "updated_at"]

    @extend_schema(
        description=_("Action for triggering an endpoint request."),
        request=serializers.RequestSerializer,
        responses={
            status.HTTP_404_NOT_FOUND: {},
            status.HTTP_202_ACCEPTED: serializers.RequestSerializer,
        },
    )
    @action(detail=True, methods=["post"], url_path="request")
    def trigger_request(self, request, *args, **kwargs) -> response.Response:  # pylint: disable=unused-argument
        """Request an endpoint with the given parameters.

        Args:
            request: The request object.

        Returns:
            The response object.
        """
        endpoint = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = async_request.delay(
            endpoint.reference,
            serializer.validated_data.get("authentication"),
            serializer.validated_data.get("params"),
            serializer.validated_data.get("headers"),
            serializer.validated_data.get("body"),
            timeout=serializer.validated_data.get("timeout"),
        )

        response_data = serializer.validated_data
        response_data["task_id"] = task.id

        return response.Response(response_data, status=status.HTTP_202_ACCEPTED)


class TraceViewSet(viewsets.ReadOnlyModelViewSet[models.Trace]):
    """Readonly viewset for :class:`compyle.proxy.models.Trace`."""

    queryset = models.Endpoint.objects.all().select_related("endpoint", "endpoint__service", "authentication")
    serializer_class = serializers.TraceSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.TraceFilterSet

    search_fields = ["reference", "endpoint__reference", "authentication__reference"]
    ordering_fields = ["reference", "status_code", "started_at", "completed_at"]


class AuthenticationViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Authentication`."""

    queryset = models.Authentication.objects.all().prefetch_related("auth_traces")
    serializer_class = serializers.AuthenticationSerializer
    serializer_classes = {}

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # filterset_class = filtersets.AuthenticationFilterSet # TODO

    search_fields = ["reference", "email"]
    ordering_fields = ["reference", "created_at", "updated_at"]

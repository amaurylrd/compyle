import secrets

from django.db.models import Count, F, Prefetch
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from requests_oauthlib import OAuth2Session
from rest_framework import filters, response, status, viewsets
from rest_framework.decorators import action

from compyle.lib.views import BaseModelViewSet
from compyle.proxy import filtersets, models, serializers
from compyle.proxy.tasks import async_request


class ServiceViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Service`."""

    queryset = models.Service.objects.all().prefetch_related("endpoints")
    serializer_class = serializers.ServiceSerializer
    serializer_classes = {
        "create": serializers.ServiceCreateSerializer,
    }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.ServiceFilterSet

    search_fields = ["reference", "name"]
    ordering_fields = ["reference", "name", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[models.Service]:
        """Returns the queryset of `Service` objects with prefetch optimization for GET requests.

        Returns:
            The queryset of `Service` objects.
        """
        queryset = super().get_queryset()

        if self.action in ("list", "retrieve"):
            queryset.prefetch_related(
                Prefetch(
                    "endpoints__endpoint_traces",
                    queryset=models.Trace.objects.only("pk"),
                )
            )

        return queryset

    @extend_schema(
        description=_("Action to get statistics across all service traces."),
        responses={
            status.HTTP_200_OK: serializers.StatisticsSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="statistics", url_name="statistics")
    def statistics(self, request, *args, **kwargs) -> response.Response:  # pylint: disable=unused-argument
        """Custom action that returns aggregated trace status counts and other statistics.

        Args:
            request: The request object.

        Returns:
            The JSON response object with statistics.
        """
        status_counter = (
            models.Trace.objects.exclude(status=None)
            .values("status")
            .annotate(name=F("status"), value=Count("pk"))
            .values("name", "value")
        )

        data = {"status_counter": status_counter}

        return response.Response(data, status=status.HTTP_200_OK)


class EndpointViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Service`."""

    queryset = models.Endpoint.objects.all().select_related("service").prefetch_related("endpoint_traces")
    serializer_class = serializers.EndpointSerializer
    serializer_classes = {
        "trigger_request": serializers.RequestSerializer,
        "authorize": serializers.AuthorizeSerialize,
        "callback": serializers.CallbackSerializer,
    }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.EndpointFilterSet

    search_fields = ["reference", "name", "service__reference"]
    ordering_fields = ["reference", "name", "created_at", "updated_at"]

    @extend_schema(
        description=_("Action for triggering an endpoint request."),
        request=serializers.RequestSerializer,
        responses={
            status.HTTP_202_ACCEPTED: serializers.RequestSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
            status.HTTP_404_NOT_FOUND: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=True, methods=["post"], url_path="request", url_name="request")
    def trigger_request(self, request, *args, **kwargs) -> response.Response:  # pylint: disable=unused-argument
        """Request an endpoint with the given parameters.

        Args:
            request: The request object.

        Returns:
            The response object.
        """
        endpoint: models.Endpoint = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = async_request.delay(
            endpoint.reference,
            serializer.data.get("authentication"),
            serializer.validated_data.get("params"),
            serializer.validated_data.get("headers"),
            serializer.validated_data.get("body"),
            timeout=serializer.validated_data.get("timeout"),
        )

        response_data = serializer.validated_data
        response_data["task_id"] = task.id

        return response.Response(response_data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        description=_("Get authorization URL for OAuth2 flow (Authorization Code Grant)."),
        request=serializers.AuthorizeSerialize,
        responses={
            status.HTTP_200_OK: serializers.AuthorizationSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
            status.HTTP_404_NOT_FOUND: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=True, methods=["post"], url_path="authorize", url_name="authorize")
    def authorize(self, request, *args, **kwargs) -> response.Response:  # pylint: disable=unused-argument
        """Initiates the OAuth2 Authorization Code flow by generating an authorization URL.

        This endpoint validates the provided authentication and redirect URI, then constructs an authorization URL
        to be used in the next step of the OAuth2 flow.

        Args:
            request: The request object.

        Returns:
            The response containing the `authorization_url` and `state` token.
        """
        endpoint: models.Endpoint = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        authentication: models.Authentication = serializer.validated_data["authentication"]

        redirect_uri = serializer.validated_data["redirect_uri"]
        oauth = OAuth2Session(
            client_id=authentication.client_id,
            redirect_uri=redirect_uri,
            scope=serializer.validated_data.get("scopes", []),
        )

        authorization_params = {
            "login_hint": serializer.validated_data.get("login_hint", authentication.email),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
        }

        authorization_url, oauth_state = oauth.authorization_url(
            endpoint.service.auth_url,
            state=serializer.validated_data.get("state") or secrets.token_urlsafe(32),
            **authorization_params,
        )

        authentication.state = oauth_state
        authentication.redirect_uri = redirect_uri
        authentication.save(update_fields=["state ", "redirect_uri"])

        serializer = serializers.AuthorizationSerializer(
            {
                "authorization_url": authorization_url,
                "state": oauth_state,
            }
        )

        return response.Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description=_("Handle the OAuth2 callback by validating the authorization code and state."),
        request=serializers.CallbackSerializer,
        responses={
            status.HTTP_200_OK: OpenApiTypes.NONE,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
            status.HTTP_404_NOT_FOUND: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=False, methods=["get"], url_path="callback", url_name="callback")
    def callback(self, request, *args, **kwargs) -> response.Response:  # pylint: disable=unused-argument
        """OAuth2 callback endpoint that receives the authorization code and state token.

        This endpoint validates the query parameters returned from the OAuth2 provider
        and associates the authorization code with the corresponding authentication entry.

        Args:
            request: The request object containing query parameters `code` and `state`.

        Returns:
            A 200 OK response if the authorization code is successfully saved.
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        state = serializer.validated_data["state"]

        authentication = get_object_or_404(models.Authentication, state=state)

        authentication.authorization_code = code
        authentication.save(update_fields=["authorization_code"])

        return response.Response(status=status.HTTP_200_OK)


class TraceViewSet(viewsets.ReadOnlyModelViewSet[models.Trace]):
    """Readonly viewset for :class:`compyle.proxy.models.Trace`."""

    queryset = models.Trace.objects.all().select_related("endpoint", "endpoint__service", "authentication")
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

    search_fields = ["reference", "email", "state"]
    ordering_fields = ["reference", "created_at", "updated_at"]

from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, response, status
from rest_framework.decorators import action

from compyle.lib.views import BaseModelViewSet
from compyle.workflow import filtersets, models, serializers


class WorkflowViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.workflow.models.Workflow`."""

    queryset = models.Workflow.objects.all().prefetch_related("steps")
    # serializer_class = serializers.WorkflowSerializer
    # serializer_classes = {
    #     "create": serializers.ServiceCreateSerializer,
    # }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.WorkflowFilterSet

    search_fields = ["reference", "name"]
    ordering_fields = ["reference", "name", "created_at", "updated_at"]

    @extend_schema(
        description=_("Action for running a workflow."),
        request=None,
        responses={
            status.HTTP_404_NOT_FOUND: {},
            status.HTTP_412_PRECONDITION_FAILED: {},
            status.HTTP_202_ACCEPTED: None,
        },
    )
    @action(detail=True, methods=["post"], url_path="run", url_name="run")
    def run(self, request, *args, **kwargs) -> response.Response:  # pylint: disable=unused-argument
        """Action for running a workflow.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            response.Response: The HTTP response object.
        """
        workflow = self.get_object()

        if not workflow.active:
            return response.Response(
                {"detail": _("Workflow is not active.")},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        response_data = {}

        return response.Response(response_data, status=status.HTTP_202_ACCEPTED)


class WorkflowStepViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.workflow.models.WorkflowStep`."""

    queryset = models.WorkflowStep.objects.all().select_related("workflow").prefetch_related("depends_on")
    # serializer_class = serializers.WorkflowStepSerializer
    # serializer_classes = {
    #     "create": serializers.ServiceCreateSerializer,
    # }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.WorkflowStepFilterSet

    search_fields = ["reference", "workflow__reference"]
    ordering_fields = ["reference", "status", "created_at", "updated_at"]

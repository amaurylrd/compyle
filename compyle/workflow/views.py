from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from compyle.lib.views import BaseModelViewSet
from compyle.workflow import filtersets, models, serializers


class WorkflowViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Workflow`."""

    queryset = models.Workflow.objects.all().prefetch_related("steps")
    # serializer_class = serializers.WorkflowSerializer
    # serializer_classes = {
    #     "create": serializers.ServiceCreateSerializer,
    # }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # filterset_class = filtersets.WorkflowFilterSet

    search_fields = ["reference", "name"]
    ordering_fields = ["reference", "name", "created_at", "updated_at"]


class WorkflowStepViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.WorkflowStep`."""

    queryset = models.WorkflowStep.objects.all().select_related("workflow").prefetch_related("depends_on")
    # serializer_class = serializers.WorkflowStepSerializer
    # serializer_classes = {
    #     "create": serializers.ServiceCreateSerializer,
    # }

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # filterset_class = filtersets.WorkflowStepFilterSet

    search_fields = ["reference", "workflow__reference"]
    ordering_fields = ["reference", "status", "created_at", "updated_at"]

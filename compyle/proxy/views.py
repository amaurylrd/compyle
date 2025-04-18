from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from compyle.lib.views import BaseModelViewSet
from compyle.proxy import filtersets, models, serializers


class ServiceViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Service`."""

    queryset = models.Service.objects.all().prefetch_related("endpoints")
    serializer_class = serializers.ServiceSerializer
    serializer_classes = {}

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.ServiceFilterSet

    search_fields = ["reference", "name"]
    ordering_fields = ["reference", "created_at", "updated_at"]

    # todo register, is_registered, get_registered


class EndpointViewSet(BaseModelViewSet):
    """Viewset for :class:`compyle.proxy.models.Service`."""

    queryset = models.Endpoint.objects.all().select_related("service").prefetch_related("traces")
    serializer_class = serializers.EndpointSerializer
    serializer_classes = {}

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.EndpointFilterSet

    search_fields = ["reference", "name", "slug"]
    ordering_fields = ["reference", "name", "created_at", "updated_at"]

    # todo request, dry_run


class TraceViewSet(viewsets.ReadOnlyModelViewSet[models.Trace]):
    """Readonly viewset for :class:`compyle.proxy.models.Trace`."""

    queryset = models.Endpoint.objects.all().select_related("endpoint")
    serializer_class = serializers.TraceSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = filtersets.TraceFilterSet

    search_fields = ["reference"]
    ordering_fields = ["reference", "status_code", "started_at", "completed_at"]


# class DynamicAPIProxyView(View):
#     def get(self, request, *args, **kwargs):
#         path_parts = request.path.strip("/").split("/")
#         if len(path_parts) < 2:
#             return JsonResponse({"error": "Invalid route"}, status=400)

#         service, endpoint = path_parts[:2]
#         query_params = request.GET.dict()
#         status, data = dispatch_request(service, endpoint, query_params)
#         return JsonResponse(data, status=status)

# class ProxyServiceView(views.ModelViewSet):
#     model =
# def get(self, request, service, resource):
#     try:
#         service_class = get_service_class(service)
#         instance = service_class()
#         result = instance.call(resource, **request.query_params)
#         return JsonResponse(result)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

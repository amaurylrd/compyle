from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from compyle.proxy import views

router = DefaultRouter()
# router.register(r"messages", views.MessageViewSet, basename="messages")
# router.register(r"traces", views.TraceViewSet, basename="traces")
# router.register(r"trace_attempts", views.TraceAttemptViewSet, basename="trace_attempts")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
]

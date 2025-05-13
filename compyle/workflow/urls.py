from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from compyle.workflow import views

router = DefaultRouter()
router.register(r"workflows", views.WorkflowViewSet, basename="workflows")
router.register(r"workflows-steps", views.WorkflowStepViewSet, basename="workflows-steps")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
]

from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from compyle.proxy import views

router = DefaultRouter()
router.register(r"services", views.ServiceViewSet, basename="services")
router.register(r"endpoints", views.EndpointViewSet, basename="endpoints")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
]

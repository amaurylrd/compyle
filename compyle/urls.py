from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path, re_path
from django.utils.translation import gettext_lazy as _
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from compyle import __version__
from compyle.proxy.urls import urlpatterns as proxy_urlpatterns

admin.site.site_title = _("Compyle")
admin.site.site_header = _("Compyle %s") % __version__

urlpatterns = [
    path("admin/", admin.site.urls),
    path("proxy/", include((proxy_urlpatterns, "proxy"), namespace="proxy")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path(".well-known/openapi", SpectacularAPIView.as_view(api_version=__version__), name="schema"),
    path(".well-known/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

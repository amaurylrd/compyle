from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path, re_path
from django.utils.translation import gettext_lazy as _
# from django.views.static import serve
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from compyle import __version__
from compyle.proxy.urls import urlpatterns as proxy_urlpatterns

admin.site.site_title = _("Compyle administration")
admin.site.site_header = _("Compyle %s") % __version__

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/openapi/", SpectacularAPIView.as_view(), name="schema"),
    path("proxy/", include((proxy_urlpatterns, "proxy"), namespace="proxy")),
]

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProxyConfig(AppConfig):
    """Configuration for the proxy app."""

    name = "compyle.proxy"
    verbose_name = _("proxy")
    verbose_name_plural = _("proxies")

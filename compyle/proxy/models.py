from django.db import models
from django.utils.translation import gettext_lazy as _

from compyle.lib.models import BaseModel, CreateUpdateMixin
from compyle.proxy.choices import AuthType, HttpMethod, StatusType
from compyle.proxy.utils import build_url, normalize_url


class Service(BaseModel, CreateUpdateMixin):
    """This class represents an external API service."""

    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("The name of the service."),
        max_length=50,
    )
    trailing_slash = models.BooleanField(
        verbose_name=_("trailing slash"),
        help_text=_("Whether to append or not a trailing slash to the url."),
        default=False,
        blank=True,
    )
    auth_type = models.CharField(
        verbose_name=_("authenfication type"),
        help_text=_("Tells how to authenticate against the service."),
        choices=AuthType.choices,
        default=AuthType.NONE,
        max_length=255,
        blank=True,
    )
    # todo token_url
    # todo refresh_token_url
    # todo auth_config

    endpoints: models.QuerySet["Endpoint"]

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self) -> str:
        return self.name


# class ServiceAuth(BaseModel):
#     # todo doc

#     api_key = models.CharField(
#         verbose_name=_("api key"),
#         help_text=_("The static API key if used.")),
#         max_length=255,
#         default=None,
#         null=True,
#         blank=True,
#     )
#     client_id = models.CharField(max_length=255, blank=True, help_text=_("OAuth2 Client ID."))
#     client_secret = models.CharField(max_length=255, blank=True, help_text=_("OAuth2 Client Secret."))

#     service = models.OneToOneField(Service, related_name="auth", on_delete=models.CASCADE)
#     class Meta:
#         verbose_name = _("service")
# #         verbose_name_plural = _("services")
# class UserCredential(BaseModel):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_credentials")
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="user_credentials")

#     access_token = models.CharField(max_length=512)
#     refresh_token = models.CharField(max_length=512, blank=True, null=True)
#     expires_at = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.user} - {self.service}"
# TODO encrypt https://git.spikeelabs.fr/spk/code/unyc/distributor/distributor-app/-/blob/main/event_broker/configuration/models.py?ref_type=heads


class Endpoint(BaseModel, CreateUpdateMixin):
    """This class represents a specific callable endpoint under a service."""

    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("The endpoint name, for a more human display."),
        max_length=255,
        unique=True,
    )
    base_url = models.URLField(
        verbose_name=_("url"),
        help_text=_("The URL of the endpoint."),
    )
    slug = models.CharField(
        verbose_name=_("slug"),
        help_text=_("The endpoint slug to be append to base URL."),
        max_length=255,
    )
    method = models.CharField(
        verbose_name=_("method"),
        help_text=_("The HTTP method used to request the endpoint with."),
        max_length=255,
        choices=HttpMethod.choices,
    )
    active = models.BooleanField(
        verbose_name=_("active"),
        help_text=_("Tells if the workflow is active."),
        default=True,
        blank=True,
    )
    json = models.BooleanField(
        verbose_name=_("json"),
        help_text=_("Indicates whether the endpoint is expected to return a JSON response."),
        default=True,
        blank=True,
    )

    service = models.ForeignKey(
        verbose_name=_("service"),
        help_text=_("The service of the endpoint."),
        to=Service,
        related_name="endpoints",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    traces: models.QuerySet["Trace"]

    class Meta:
        verbose_name = _("endpoint")
        verbose_name_plural = _("endpoints")

    def __str__(self) -> str:
        return self.name

    def build_url(self, **params) -> str:
        """Builds the URL for the specified queryset.

        Args:
            **params: The parameters of the query.


        Returns:
            The normalized unparsed URL built with the specified query parameters.
        """
        return normalize_url(build_url(self.base_url, self.slug, **params), self.service.trailling_slash)


class Trace(BaseModel):
    """This class sepresents a trace of an HTTP request and response for debugging, logging, or auditing purposes."""

    started_at = models.DateTimeField(
        verbose_name=_("started at"),
        help_text=_("The datetime of the request."),
        auto_now_add=True,
    )
    completed_at = models.DateTimeField(
        verbose_name=_("completed at"),
        help_text=_("The datetime of the response, if any."),
        default=None,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name=_("status"),
        help_text=_("The status name of the request response."),
        max_length=50,
    )
    status_code = models.IntegerField(
        verbose_name=_("status code"),
        help_text=_("The status code of the request response."),
    )
    status_type = models.CharField(
        verbose_name=_("status type"),
        help_text=_("The category of the resposne status code."),
        choices=StatusType.choices,
        max_length=255,
        default=None,
        null=True,
    )
    headers = models.JSONField(
        verbose_name=_("headers"),
        help_text=_("The headers associated with the HTTP request or response."),
        blank=True,
        null=True,
    )
    payload = models.JSONField(
        verbose_name=_("payload"),
        help_text=_("The body of the request or response JSON-formatted."),
        blank=True,
        null=True,
    )

    endpoint = models.ForeignKey(
        verbose_name=_("endpoint"),
        help_text=_("The endpoint of the trace."),
        to=Endpoint,
        related_name="traces",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("trace")
        verbose_name_plural = _("traces")
        ordering = ["started_at"]

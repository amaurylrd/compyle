from django.db import models
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt

from compyle.lib.models import BaseModel, CreateUpdateMixin
from compyle.proxy.choices import AuthFlow, AuthMethod, HttpMethod, StatusType
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
    auth_flow = models.CharField(
        verbose_name=_("authenfication type"),
        help_text=_("Tells how to authenticate against the service."),
        choices=AuthFlow.choices,
        default=None,
        null=True,
        blank=True,
        max_length=255,
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
    auth_method = models.CharField(
        verbose_name=_("authenfication method"),
        help_text=_("The authification method to be used."),
        choices=AuthMethod.choices,
        default=None,
        null=True,
        blank=True,
        max_length=255,
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
    endpoint_traces: models.QuerySet["Trace"]

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
        help_text=_("The category of the response status code."),
        choices=StatusType.choices,
        max_length=255,
        default=None,
        null=True,
    )
    headers = models.JSONField(
        verbose_name=_("headers"),
        help_text=_("The headers associated with the HTTP request or response."),
        default=dict,
        blank=True,
        null=True,
    )
    payload = models.JSONField(
        verbose_name=_("payload"),
        help_text=_("The body of the request or response JSON-formatted."),
        default=None,
        blank=True,
        null=True,
    )
    # TODO params

    endpoint = models.ForeignKey(
        verbose_name=_("endpoint"),
        help_text=_("The endpoint of the trace."),
        to=Endpoint,
        related_name="endpoint_traces",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name=_("user"),
        help_text=_("The authenficiation provided for the trace."),
        to="AuthUser",
        related_name="user_traces",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name = _("trace")
        verbose_name_plural = _("traces")
        ordering = ["started_at"]


class AuthUser(BaseModel, CreateUpdateMixin):
    # TODO docstring

    email = models.CharField(
        verbose_name=_("email"),
        help_text=_("The user unique email."),
        unique=True,
        max_length=255,
    )
    login = encrypt(
        models.CharField(
            verbose_name=_("login"),
            help_text=_("The user login issued to the client during the application registration process."),
            max_length=255,
            default=None,
            null=True,
            blank=True,
        )
    )
    password = encrypt(
        models.CharField(
            verbose_name=_("password"),
            help_text=_("The user password issued to the client during the application registration process."),
            max_length=255,
            default=None,
            null=True,
            blank=True,
        )
    )
    client_id = encrypt(
        models.CharField(
            verbose_name=_("client id"),
            help_text=_("The client identifier issued to the client during the application registration process."),
            max_length=255,
            default=None,
            null=True,
            blank=True,
        )
    )
    client_secret = encrypt(
        models.CharField(
            verbose_name=_("client secret"),
            help_text=_("The client secret issued to the client during the application registration process."),
            max_length=255,
            default=None,
            null=True,
            blank=True,
        )
    )
    api_key = encrypt(
        models.CharField(
            verbose_name=_("api key"),
            help_text=_("The static API key."),
            max_length=255,
            default=None,
            null=True,
            blank=True,
        )
    )

    # TODO
    # autorization_code (add encrypt?)
    # token_type
    # redirect_uri

    # todo add encrypt ?
    access_token = models.CharField(
        verbose_name=_("access token"),
        help_text=_("The access token to be used for authentication."),
        max_length=512,
        default=None,
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(
        verbose_name=("expires at"),
        help_text=_("The datetime the access token will expire."),
        default=None,
        blank=True,
        null=True,
    )
    refresh_token = models.CharField(
        verbose_name=_("refresh token"),
        help_text=_("The refresh token to be used for refreshing the access token."),
        max_length=512,
        default=None,
        null=True,
        blank=True,
    )

    user_traces: models.QuerySet["Trace"]

    class Meta:
        verbose_name = _("authentication user")
        verbose_name_plural = _("authentication users")


# TODO lien entre user / trace ?
# TODO method request header selon auth_flow / auth_method
# TODO comment dire d'ajouter le client_id dans le header par example

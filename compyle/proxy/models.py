from functools import cached_property
from typing import Any

import requests
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt

from compyle.lib.models import BaseModel, CreateUpdateMixin
from compyle.proxy import choices
from compyle.proxy.utils import build_url, normalize_url, request_with_retry


class Service(BaseModel, CreateUpdateMixin):
    """This class represents an external API service."""

    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("The name of the service, for a more human display."),
        max_length=100,
    )
    documentation_url = models.URLField(
        verbose_name=_("documentation URL"),
        help_text=_("The URL of the API documentation."),
        default=None,
        null=True,
        blank=True,
    )
    trailing_slash = models.BooleanField(
        verbose_name=_("trailing slash"),
        help_text=_("Whether to append or not a trailing slash to the url."),
        default=False,
        blank=True,
    )
    auth_flow = models.CharField(
        verbose_name=_("authenfication flow"),
        help_text=_("Tells how to authenticate against the service. If not set, no authentication will be used."),
        choices=choices.AuthFlow.choices,
        default=None,
        null=True,
        blank=True,
        max_length=255,
    )
    token_url = models.URLField(
        verbose_name=_("token URL"),
        help_text=_("The URL to be used to request or refresh the user token."),
        default=None,
        null=True,
        blank=True,
    )
    auth_url = models.URLField(
        verbose_name=_("authorization URL"),
        help_text=_("The URL to be used to get the user authorization code."),
        default=None,
        null=True,
        blank=True,
    )

    endpoints: models.QuerySet["Endpoint"]

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self) -> str:
        return str(self.name)


class Endpoint(BaseModel, CreateUpdateMixin):
    """This class represents a specific callable endpoint under a service."""

    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("The endpoint name, for a more human display."),
        max_length=100,
    )
    base_url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("The URL of the endpoint."),
    )
    slug = models.CharField(
        verbose_name=_("slug"),
        help_text=_("The endpoint slug to be append to base URL."),
        max_length=50,
    )
    method = models.CharField(
        verbose_name=_("method"),
        help_text=_("The HTTP method used to request the endpoint with."),
        max_length=10,
        choices=choices.HttpMethod.choices,
    )
    response_type = models.CharField(
        verbose_name=_("response type"),
        help_text=_("Indicates the expected response format."),
        max_length=10,
        choices=choices.ResponseType.choices,
        default=choices.ResponseType.JSON,
    )
    auth_method = models.CharField(
        verbose_name=_("authenfication method"),
        help_text=_("The authification method to be used."),
        choices=choices.AuthMethod.choices,
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
        on_delete=models.CASCADE,
    )
    endpoint_traces: models.QuerySet["Trace"]

    class Meta:
        verbose_name = _("endpoint")
        verbose_name_plural = _("endpoints")

    def __str__(self) -> str:
        return str(self.name)

    def update_headers(self, headers: dict[str, str]) -> None:
        """Build headers appropriate Content-Type and Accept headers properties based on the expected response type.

        Args:
            headers: The headers specified by the user.
        """
        if self.response_type == choices.ResponseType.JSON:
            content_type = "application/json"
        elif self.response_type == choices.ResponseType.XML:
            content_type = "application/xml"
        else:
            content_type = "text/plain"

        headers.update(
            {
                "Content-Type": content_type,
                "Accept": content_type,
            }
        )

    def build_url(self, **params) -> str:
        """Builds the URL for the specified queryset.

        Args:
            **params: The parameters of the query.

        Returns:
            The normalized unparsed URL built with the specified query parameters.
        """
        return normalize_url(build_url(self.base_url, self.slug, **params), self.service.trailing_slash)

    def request(
        self,
        url: str,
        headers: dict[str, str] = None,
        body: dict[str, Any] = None,
        **kwargs,
    ) -> requests.Response:
        """Request the endpoint with the specified parameters.

        Args:
            url: The URL to be used for the request.
            headers: The headers to be used for the request. Defaults to None.
            body: The body to be used for the request. Defaults to None.
            **kwargs: Additional arguments for `requests.request`, such as `timeout`, `auth`, `json`, `cookies`...

        Returns:
            The response of the request.
        """
        return request_with_retry(choices.HttpMethod(self.method), url, headers=headers, data=body, **kwargs)

    def parse_response(self, response: requests.Response) -> Any:
        """Parse the response based on the expected content type.

        Args:
            response: The response to be parsed.

        Returns:
            The parsed response content.
        """
        if self.response_type == choices.ResponseType.JSON:
            return response.json()
        if self.response_type == choices.ResponseType.XML:
            return response.content
        return response.text


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
    method = models.CharField(
        verbose_name=_("method"),
        help_text=_("The HTTP method used to request the endpoint with."),
        max_length=10,
        choices=choices.HttpMethod.choices,
    )
    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("The URL of the request."),
        default=None,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name=_("status"),
        help_text=_("The status of the request response."),
        max_length=3,
        choices=choices.HttpStatus.choices,
        null=True,
        blank=True,
        default=None,
    )
    status_code = models.IntegerField(
        verbose_name=_("status code"),
        help_text=_("The status code of the request response."),
        default=None,
        null=True,
        blank=True,
    )
    headers = models.JSONField(
        verbose_name=_("headers"),
        help_text=_("The headers associated with the HTTP request."),
        default=dict,
        blank=True,
        null=True,
    )
    payload = models.JSONField(
        verbose_name=_("payload"),
        help_text=_("The body of the request JSON-formatted."),
        default=None,
        blank=True,
        null=True,
    )
    response = models.CharField(
        verbose_name=_("response"),
        help_text=_("The parsed response based on the expected content type."),
        default=None,
        blank=True,
        null=True,
    )

    endpoint = models.ForeignKey(
        verbose_name=_("endpoint"),
        help_text=_("The endpoint of the trace."),
        to=Endpoint,
        related_name="endpoint_traces",
        on_delete=models.CASCADE,
    )
    authentication = models.ForeignKey(
        verbose_name=_("authentication"),
        help_text=_("The authentication provided for the trace."),
        to="Authentication",
        related_name="auth_traces",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("trace")
        verbose_name_plural = _("traces")
        ordering = ["started_at"]

    def save(self, *args, **kwargs) -> None:
        """Overrides the default save method to automatically update the `status` field
        based on the current `status_code` before saving the model instance.
        """
        if self.status_code is not None:
            self.status = choices.HttpStatus.from_status_code(self.status_code).value

        super().save(*args, **kwargs)


class Authentication(BaseModel, CreateUpdateMixin):
    """This class represents an authentication to be used for a specific endpoint call."""

    email = models.CharField(
        verbose_name=_("email"),
        help_text=_("The user email."),
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
    state = models.CharField(
        verbose_name=_("state"),
        help_text=_("The OAuth2 state to maintain state between authorization request and callback."),
        max_length=64,
        blank=True,
        null=True,
        unique=True,
    )
    redirect_uri = models.URLField(
        verbose_name=_("redirect URI"),
        help_text=_("One of the OAuth2 redirect URIs listed for the given client_id."),
        default=None,
        blank=True,
        null=True,
    )
    authorization_code = encrypt(
        models.CharField(
            verbose_name=_("authorization code"),
            help_text=_("The code received from OAuth2 provider to exchange for access token."),
            max_length=255,
            default=None,
            blank=True,
            null=True,
        )
    )
    access_token = encrypt(
        models.CharField(
            verbose_name=_("access token"),
            help_text=_("The access token to be used for authentication."),
            max_length=512,
            default=None,
            null=True,
            blank=True,
        )
    )
    expires_at = models.DateTimeField(
        verbose_name=("expires at"),
        help_text=_("The datetime the access token will expire."),
        default=None,
        blank=True,
        null=True,
    )
    refresh_token = encrypt(
        models.CharField(
            verbose_name=_("refresh token"),
            help_text=_("The refresh token to be used for refreshing the access token."),
            max_length=512,
            default=None,
            null=True,
            blank=True,
        )
    )

    auth_traces: models.QuerySet["Trace"]

    class Meta:
        verbose_name = _("authentication")
        verbose_name_plural = _("authentications")

    def __str__(self) -> str:
        return str(self.email)

    @cached_property
    @admin.display(description=_("is token valid"), boolean=True)
    def is_token_valid(self) -> bool:
        """Check whether the access token is still valid.

        Returns:
            True if the access token exists and has not expired, False otherwise.
        """
        return bool(self.access_token and self.expires_at and self.expires_at > timezone.now())

    def update_token(self, token: dict[str, Any]) -> None:
        """Update the access token and refresh token.

        Args:
            token: The token dictionary containing the access token and refresh token.
        """
        self.access_token = token["access_token"]
        self.refresh_token = token.get("refresh_token")
        self.expires_at = timezone.now() + timezone.timedelta(seconds=token.get("expires_in", 3600))
        self.save(update_fields=["access_token", "refresh_token", "expires_at"])

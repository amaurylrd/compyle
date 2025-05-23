from collections.abc import Callable
from typing import Any

import requests
from django.db.models import TextChoices
from django.utils.translation import pgettext_lazy


class HttpMethod(TextChoices):
    """This enum represents the HTTP methods supported by the API."""

    GET = "get", pgettext_lazy("http method", "GET")
    POST = "post", pgettext_lazy("http method", "POST")
    PUT = "put", pgettext_lazy("http method", "PUT")
    PATCH = "patch", pgettext_lazy("http method", "PATCH")
    DELETE = "delete", pgettext_lazy("http method", "DELETE")

    @property
    def func(self) -> Callable[..., Any]:
        """Retrieve the partial function from its enum name.

        Returns:
            the function callable if the attribute exists, raises an error otherwise.
        """
        return getattr(requests, self.value)

    def __call__(self, *args, **kwargs) -> requests.Response:  # type: ignore[no-untyped-def]
        """Calls the function associated with the enum.

        Returns:
            the result of the function.
        """
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        """Returns the representation of the enum.

        Returns:
            str: the representation of the enum.
        """
        return self.func.__repr__()

    def __str__(self) -> str:
        """Returns the string representation of the enum.

        Returns:
            str: the string representation of the enum.
        """
        return self.func.__str__()


class ResponseType(TextChoices):
    """This enum represents the response types supported by the API."""

    JSON = "json", pgettext_lazy("response type", "JSON")
    XML = "xml", pgettext_lazy("response type", "XML")
    RAW = "raw", pgettext_lazy("response type", "RAW")


class AuthFlow(TextChoices):
    """This enum represents high-level authentication flow supported by a service."""

    API_KEY = "api_key", pgettext_lazy("authentication flow", "API key")
    BASIC_AUTHENTICATION = "basic_authentication", pgettext_lazy("authentication flow", "Basic authentication")
    OAUTH2_AUTHORIZATION_CODE = "authorization code", pgettext_lazy("authentication flow", "Authorization code")
    OAUTH2_ClIENT_CREDENTIALS = "client credentials", pgettext_lazy("authentication flow", "Client credentials")


class AuthMethod(TextChoices):
    """This specific authentication mechanisms used at the endpoint level."""

    OAUTH_PASSWORD_AUTHENTICATION = "oauth_password_authentication", pgettext_lazy(
        "authentication method", "OAuth authentication (grant type 'password')"
    )
    OAUTH_CLIENT_CREDENTIALS_AUTHENTICATION = "oauth_client_credentials_authentication", pgettext_lazy(
        "authentication method", "OAuth authentication (grant type 'client_credentials')"
    )

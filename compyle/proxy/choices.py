from collections.abc import Callable
from typing import Any

import requests
from django.db.models import TextChoices
from django.utils.translation import pgettext_lazy


class HttpMethod(TextChoices):
    """This enum represents the HTTP methods supported by the API."""

    HEAD = "head", pgettext_lazy("http method", "HEAD")
    GET = "get", pgettext_lazy("http method", "GET")
    POST = "post", pgettext_lazy("http method", "POST")
    PUT = "put", pgettext_lazy("http method", "PUT")
    PATCH = "path", pgettext_lazy("http method", "PATCH")
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


class AuthFlow(TextChoices):
    """This enum represents high-level authentication flow supported by a service."""

    API_KEY = "api_key", pgettext_lazy("authentication type", "API key")
    BASIC_AUTHENTICATION = "basic_authentication", pgettext_lazy("authentication type", "Basic authentication")
    OAUTH2_AUTHORIZATION_CODE = "authorization code", pgettext_lazy("authentication type", "Authorization code")
    OAUTH2_ClIENT_CREDENTIALS = "client credentials", pgettext_lazy("authentication type", "Client credentials")


class AuthMethod(TextChoices):
    """This specific authentication mechanisms used at the endpoint level."""

    OAUTH_PASSWORD_AUTHENTICATION = "oauth_password_authentication", pgettext_lazy(
        "authentication method", "OAuth authentication (grant type 'password')"
    )
    OAUTH_CLIENT_CREDENTIALS_AUTHENTICATION = "oauth_client_credentials_authentication", pgettext_lazy(
        "authentication method", "OAuth authentication (grant type 'client_credentials')"
    )


# twitch
# - get_token = grant_type: client_cred
# - refresh = auth: bearer OAuth2 token

# yt
# get_token: grant_type: authorizatin_code
# refresh: grant_type refresh

# TODO https://git.spikeelabs.fr/spk/code/unyc/distributor/distributor-app/-/blob/main/event_broker/traceability/components/auth.py

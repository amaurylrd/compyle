from collections.abc import Callable
from typing import Any

import requests
from django.db.models import TextChoices
from django.utils.translation import pgettext_lazy
from rest_framework import status


class HttpMethod(TextChoices):
    """This enum represents the HTTP methods supported by the API."""

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


class StatusType(TextChoices):
    """This enum represents response status type from the status code."""

    INFORMATIONAL = "informational", pgettext_lazy("status type", "Informational")
    SUCCESS = "success", pgettext_lazy("status type", "Success")
    REDIRECT = "redirect", pgettext_lazy("status type", "Redirect")
    CLIENT_ERROR = "client_error", pgettext_lazy("status type", "Client error")
    SERVER_ERROR = "server_error", pgettext_lazy("status type", "Server error")

    @classmethod
    def from_code(cls, status_code: int) -> "StatusType":
        """Returns the status category based on the HTTP status code.

        Args:
            status_code (int): The HTTP status code.

        Returns:
            StatusType: Corresponding category as a string.
        """
        if status.is_informational(status_code):
            return cls.INFORMATIONAL
        if status.is_success(status_code):
            return cls.SUCCESS
        if status.is_redirect(status_code):
            return cls.REDIRECT
        if status.is_client_error(status_code):
            return cls.CLIENT_ERROR
        if status.is_server_error(status_code):
            return cls.SERVER_ERROR
        return None


class AuthType(TextChoices):
    """This enum represents high-level authentication types supported by a service."""

    NONE = "none", pgettext_lazy("authentification type", "No Auth")
    API_KEY = "api_key", pgettext_lazy("authentification type", "API Key")
    BEARER = "bearer", pgettext_lazy("authentification type", "Bearer Token")
    OAUTH2 = "oauth2", pgettext_lazy("authentification type", "OAuth2")


class AuthMethod(TextChoices):
    """This specific authentication mechanisms used at the endpoint level."""

    NO_AUTHENTICATION = "no_authentication", pgettext_lazy("authentication method", "No authentication")
    BASIC_AUTHENTICATION = "basic_authentication", pgettext_lazy("authentication method", "Basic authentication")
    OAUTH_PASSWORD_AUTHENTICATION = "oauth_password_authentication", pgettext_lazy(
        "authentication method", "OAuth authentication (grant type 'password')"
    )
    OAUTH_CLIENT_CREDENTIALS_AUTHENTICATION = "oauth_client_credentials_authentication", pgettext_lazy(
        "authentication method", "OAuth authentication (grant type 'client_credentials')"
    )


# TODO https://git.spikeelabs.fr/spk/code/unyc/distributor/distributor-app/-/blob/main/event_broker/traceability/components/auth.py

from typing import Callable, Any

import requests
from django.db.models import TextChoices
from django.utils.translation import pgettext_lazy


class HttpMethod(TextChoices):
    """This enum represents the HTTP methods supported by the API."""

    POST = "POST", pgettext_lazy("http method", "POST")
    PUT = "PUT", pgettext_lazy("http method", "PUT")
    PATCH = "PATCH", pgettext_lazy("http method", "PATCH")
    DELETE = "DELETE", pgettext_lazy("http method", "DELETE")

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

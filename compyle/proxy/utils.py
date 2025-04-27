from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from requests.adapters import HTTPAdapter
from rest_framework import status
from urllib3.util import Retry

from compyle.proxy.choices import HttpMethod


def extract_url_params(url: str) -> list[tuple[str, str]]:
    """Extracts the parameters from the specified URL.

    Args:
        url: The URL to extract the parameters from.

    Returns:
        The list of parameters, as G-d intended.
    """
    return parse_qsl(urlparse(url).query, keep_blank_values=True)


def add_url_params(url: str, **params) -> str:
    """Adds the specified parameters to the URL.

    Args:
        url: The URL to add the parameters to.
        **params: The parameters to be added.

    Returns:
        The url with the parameters added.
    """
    parts = urlparse(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True)).update(params)

    return urlunparse(parts._replace(query=urlencode(query)))


def build_url(url: str, slug: str, **params) -> str:
    """Builds the URL for the specified queryset.

    Args:
        url: The base URL.
        slug: The slug for that URL.
        **params: The parameters of the query.

    Returns:
        The unparsed URL built with the normalized query parameters.
    """
    components = list(urlparse(url, allow_fragments=False))
    components[2] += slug
    components[4] = urlencode(params)

    return urlunparse(components)


def normalize_url(url: str, trailling_slash: bool) -> str:
    """Normalize a URL's trailing slash based on a flag.

    Args:
        url: The input URL to normalize.
        trailing_slash: If True, ensures the URL ends with a slash, otherwise removes the trailing slash if present.

    Returns:
        The normalized URL with or without a trailing slash.
    """
    # adds a trailing slash if the option is specified and the url does not already end with a slash
    if trailling_slash and url[-1] != "/":
        return url + "/"

    # removes the trailing slash if the option is not specified and the url ends with a slash
    if not trailling_slash and url[-1] == "/":
        return url[:-1]

    return url


def request_with_retry(
    method: HttpMethod,
    url: str,
    retries: int = 3,
    backoff: float | None = 0.5,
    jitter: float | None = 0.5,
    timeout: float | None = None,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> requests.Response:
    with requests.Session() as session:
        strategery = Retry(
            total=retries,
            backoff_factor=backoff,
            backoff_jitter=jitter,
            status_forcelist=[
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                status.HTTP_502_BAD_GATEWAY,
                status.HTTP_503_SERVICE_UNAVAILABLE,
                status.HTTP_504_GATEWAY_TIMEOUT,
            ],
        )
        adapter = HTTPAdapter(max_retries=strategery)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        try:
            response: requests.Response = method(url, headers=headers, data=body, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise error

        return response

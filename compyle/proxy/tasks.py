import logging
from typing import Any

from celery import shared_task

LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument, too-many-locals, too-many-arguments
@shared_task(bind=True)
def async_request(
    self,
    endpoint_id: str,
    authentication_id: str | None,
    params: dict[str, str],
    headers: dict[str, str],
    body: dict[str, Any] | None,
    timeout: float | None = None,
    commit: bool = True,
) -> Any:
    """Perform an asynchronous HTTP request to a specified endpoint with optional authentication.

    Args:
        self: The task instance (automatically passed by Celery).
        endpoint_id: The reference ID of the Endpoint to request.
        authentication_id: The reference ID of the Authentication object or None.
        params: The URL parameters to be applied to the endpoint URL.
        headers: The HTTP headers to include in the request.
        body: The request payload for methods like POST or PUT or None.
        timeout: Optional timeout in seconds for the request. Defaults to None.
        commit: Flag to enable tracing. Defaults to True.

    Returns:
       The parsed response from the endpoint.

    Raises:
        Endpoint.DoesNotExist: If the endpoint with the given ID does not exist.
        Authentication.DoesNotExist: If the authentication with the given ID does not exist.
        requests.exceptions.HTTPError: Requests exceptions may propagate if the HTTP request fails.
    """
    # pylint: disable=import-outside-toplevel
    import requests

    from compyle.proxy.choices import AuthFlow
    from compyle.proxy.models import Authentication, Endpoint, Trace

    endpoint = Endpoint.objects.get(reference=endpoint_id)
    authentication = basic_auth = None

    endpoint.update_headers(headers)

    if authentication_id:
        authentication = Authentication.objects.get(reference=authentication_id)

        if endpoint.service.auth_flow == AuthFlow.API_KEY:
            headers["Authorization"] = f"Bearer {authentication.api_key}"
            headers["x-api-key"] = authentication.api_key

        elif endpoint.service.auth_flow == AuthFlow.OAUTH2_CLIENT_CREDENTIALS:
            if not authentication.is_token_valid:
                if authentication.refresh_token:
                    response = requests.post(
                        endpoint.service.token_url,
                        data={
                            "grant_type": "refresh_token",
                            "refresh_token": authentication.refresh_token,
                            "client_id": authentication.client_id,
                            "client_secret": authentication.client_secret,
                        },
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json",
                        },
                        timeout=60,
                    )
                else:
                    response = requests.post(
                        endpoint.service.token_url,
                        data={
                            "client_id": authentication.client_id,
                            "client_secret": authentication.client_secret,
                            "grant_type": "client_credentials",
                        },
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json",
                        },
                        timeout=60,
                    )

                response.raise_for_status()
                token = response.json()
                authentication.update_token(token)

            headers["Client-ID"] = authentication.client_id
            headers["Authorization"] = f"Bearer {authentication.access_token}"

        elif endpoint.service.auth_flow == AuthFlow.OAUTH2_AUTHORIZATION_CODE:
            if not authentication.is_token_valid:
                response = requests.post(
                    endpoint.service.token_url,
                    data={
                        "client_id": authentication.client_id,
                        "client_secret": authentication.client_secret,
                        "code": authentication.authorization_code,
                        "redirect_uri": authentication.redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                    },
                    timeout=60,
                )

                response.raise_for_status()
                token = response.json()
                # TODO add scope to authentication + dans l'amin
                authentication.update_token(token)

        elif endpoint.service.auth_flow == AuthFlow.BASIC_AUTHENTICATION:
            from requests.auth import HTTPBasicAuth

            basic_auth = HTTPBasicAuth(authentication.login, authentication.password)

    url = endpoint.build_url(**params)

    # if hasattr(endpoint.service, 'token_headers') and endpoint.service.token_headers:
    # token_headers.update(endpoint.service.token_headers)

    if commit:
        trace = Trace(
            endpoint=endpoint,
            authentication=authentication,
            method=endpoint.method,
            url=url,
            headers=headers,
            payload=body,
        )
        trace.save()

    response = endpoint.request(url, headers=headers, body=body, auth=basic_auth, timeout=timeout)
    parsed_response = endpoint.parse_response(response)

    if commit:
        trace.response = parsed_response
        trace.completed_at = trace.started_at + response.elapsed
        trace.status_code = response.status_code
        trace.save(update_fields=["response", "completed_at", "status_code", "status"])

    return parsed_response

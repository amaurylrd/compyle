from typing import Any

from celery import shared_task
from requests_oauthlib import OAuth2Session


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

    Returns:
       The parsed response from the endpoint.

    Raises:
        Endpoint.DoesNotExist: If the endpoint with the given ID does not exist.
        Authentication.DoesNotExist: If the authentication with the given ID does not exist.
        Requests exceptions may propagate if the HTTP request fails.
    """
    # pylint: disable=import-outside-toplevel
    from compyle.proxy.choices import AuthFlow
    from compyle.proxy.models import Authentication, Endpoint, Trace

    endpoint = Endpoint.objects.get(reference=endpoint_id)
    authentication = None

    if authentication_id:
        authentication = Authentication.objects.get(reference=authentication_id)

        if endpoint.service.auth_flow == AuthFlow.API_KEY:
            headers["Authorization"] = f"Bearer {authentication.api_key}"
            # x-api-key header ?

        elif endpoint.service.auth_flow == AuthFlow.OAUTH2_ClIENT_CREDENTIALS:
            oauth = OAuth2Session(client_id=authentication.client_id)

            if authentication.is_token_valid:
                pass
            elif authentication.refresh_token:
                token = oauth.refresh_token(
                    endpoint.service.token_url,
                    client_id=authentication.client_id,
                    client_secret=authentication.client_secret,
                    refresh_token=authentication.refresh_token,
                )
                authentication.update_token(token)
            else:
                token = oauth.fetch_token(
                    token_url=endpoint.service.token_url,
                    client_id=authentication.client_id,
                    client_secret=authentication.client_secret,
                )
                authentication.update_token(token)

            headers["Client-ID"] = authentication.client_id
            headers["Authorization"] = f"Bearer {authentication.access_token}"

        elif endpoint.service.auth_flow == AuthFlow.OAUTH2_AUTHORIZATION_CODE:
            pass
        elif endpoint.service.auth_flow == AuthFlow.BASIC_AUTHENTICATION:
            pass

    url = endpoint.build_url(**params)

    trace = Trace(
        endpoint=endpoint,
        authentication=authentication,
        method=endpoint.method,
        url=url,
        headers=headers,
        payload=body,
    )
    trace.save()

    response = endpoint.request(url, headers=headers, body=body, timeout=timeout)

    trace.completed_at = trace.started_at + response.elapsed
    trace.status_code = response.status_code
    trace.save()

    return endpoint.parse_response(response)

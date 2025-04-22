from datetime import datetime

from faker import Faker

from compyle.lib.factories import DEFAULT, sequence
from compyle.proxy import choices, models

_FAKER = Faker()
SERVICE_REFERENCE_SEQUENCE = sequence(lambda i: f"auto-service-{i}")
ENDPOINT_REFERENCE_SEQUENCE = sequence(lambda i: f"auto-endpoint-{i}")
TRACE_REFERENCE_SEQUENCE = sequence(lambda i: f"auto-trace-{i}")
USER_REFERENCE_SEQUENCE = sequence(lambda i: f"auto-user-{i}")


def get_service(
    *,
    commit: bool = DEFAULT,
    reference: str = DEFAULT,
    name: str = DEFAULT,
    trailing_slash: bool = DEFAULT,
    auth_flow: choices.AuthFlow | None = DEFAULT,
) -> models.Service:
    if commit is DEFAULT:
        commit = True

    if reference is DEFAULT:
        reference = next(SERVICE_REFERENCE_SEQUENCE)

    if name is DEFAULT:
        name = _FAKER.word()
    if trailing_slash is DEFAULT:
        trailing_slash = True
    if auth_flow is DEFAULT:
        auth_flow = None

    service = models.Service(
        reference=reference,
        name=name,
        trailing_slash=trailing_slash,
        auth_flow=auth_flow,
    )

    if commit:
        service.save()

    return service


def get_endpoint(
    *,
    commit: bool = DEFAULT,
    commit_related: bool = DEFAULT,
    reference: str = DEFAULT,
    base_url: str = DEFAULT,
    slug: str = DEFAULT,
    method: choices.HttpMethod = DEFAULT,
    active: bool = DEFAULT,
    json: bool = DEFAULT,
    auth_method: choices.AuthMethod | None = DEFAULT,
    service: models.Service = DEFAULT,
) -> models.Endpoint:
    if commit_related is DEFAULT:
        commit_related = True
    if commit is DEFAULT:
        commit = commit_related
    if commit and not commit_related:  # pragma: no cover
        raise ValueError("cannot commit when related models are not committed")

    if reference is DEFAULT:
        reference = next(ENDPOINT_REFERENCE_SEQUENCE)

    if base_url is DEFAULT:
        base_url = _FAKER.url()
    if slug is DEFAULT:
        slug = _FAKER.word()
    if method is DEFAULT:
        method = choices.HttpMethod.GET
    if active is DEFAULT:
        active = True
    if json is DEFAULT:
        json = True
    if auth_method is DEFAULT:
        auth_method = None

    if service is DEFAULT:
        service = get_service(commit=commit_related)

    endpoint = models.Endpoint(
        reference=reference,
        base_url=base_url,
        slug=slug,
        method=method,
        active=active,
        json=json,
        auth_method=auth_method,
        service=service,
    )

    if commit:
        endpoint.save()

    return endpoint


def get_trace(
    *,
    commit: bool = DEFAULT,
    commit_related: bool = DEFAULT,
    reference: str = DEFAULT,
    started_at: datetime = DEFAULT,
    completed_at: datetime = DEFAULT,
    status: str = DEFAULT,
    status_code: int = DEFAULT,
    status_type: choices.StatusType | None = DEFAULT,
    headers: dict = DEFAULT,
    payload: dict = DEFAULT,
    endpoint: models.Endpoint = DEFAULT,
    user: models.AuthUser = DEFAULT,
) -> models.Trace:
    if commit_related is DEFAULT:
        commit_related = True
    if commit is DEFAULT:
        commit = commit_related
    if commit and not commit_related:  # pragma: no cover
        raise ValueError("cannot commit when related models are not committed")

    if reference is DEFAULT:
        reference = next(TRACE_REFERENCE_SEQUENCE)

    # todo
    if started_at is DEFAULT:
        pass
    if completed_at is DEFAULT:
        pass
    if status is DEFAULT:
        pass
    if status_code is DEFAULT:
        pass
    if status_type is DEFAULT:
        status_type = None
    if headers is DEFAULT:
        headers = {}
    if payload is DEFAULT:
        payload = None

    if endpoint is DEFAULT:
        endpoint = get_endpoint(commit=commit_related)
    if user is DEFAULT:
        user = get_user(commit=commit_related)

    trace = models.Trace(
        reference=reference,
        status=status,
        status_code=status_code,
        status_type=status_type,
        headers=headers,
        payload=payload,
        endpoint=endpoint,
        user=user,
    )

    if commit:
        trace.save()

    return trace


def get_user(
    *,
    commit: bool = DEFAULT,
    reference: str = DEFAULT,
) -> models.AuthUser:
    if commit is DEFAULT:
        commit = True

    if reference is DEFAULT:
        reference = next(USER_REFERENCE_SEQUENCE)

    user = models.AuthUser(
        reference=reference,
    )

    if commit:
        user.save()

    return user

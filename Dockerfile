FROM python:3.10-slim-bookworm

ARG POETRY_VERSION=1.5.1
ARG PIP_VERSION=23.2.1
ARG GETTEXT_VERSION=0.21-12

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    DJANGO_SETTINGS_MODULE=compyle.settings

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Install system dependencies and gettext
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gettext=${GETTEXT_VERSION} build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python and Poetry dependencies
RUN python -m pip install --upgrade pip virtualenv && \
    pip install --no-cache-dir --upgrade pip==${PIP_VERSION} && \
    pip install --no-cache-dir poetry==${POETRY_VERSION}

COPY . .

# Install application dependencies (only main group)
RUN poetry install --only main --no-interaction --no-ansi && \
    rm -rf /root/.cache/pypoetry /root/.local /usr/local/bin/poetry

# Install static files and compile messages
RUN python manage.py collectstatic --noinput
# TODO python manage.py compilemessages --settings=$DJANGO_SETTINGS_MODULE

EXPOSE 8000

CMD ["gunicorn", "compyle.wsgi", "-c", "gunicorn.py"]

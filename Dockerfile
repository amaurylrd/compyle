# FROM python:3.10.12-slim-bookworm AS python-base

# ARG POETRY_HTTP_BASIC_REGISTRYCOMMON_USERNAME
# ARG POETRY_HTTP_BASIC_REGISTRYCOMMON_PASSWORD
# ARG POETRY_VERSION=1.5.1
# ARG PIP_VERSION=23.2.1
# ARG GETTEXT_VERSION=0.21-12

# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PIP_NO_CACHE_DIR=off \
#     PIP_DISABLE_PIP_VERSION_CHECK=on \
#     PIP_DEFAULT_TIMEOUT=100 \
#     POETRY_VIRTUALENVS_CREATE=false \
#     POETRY_VIRTUALENVS_IN_PROJECT=false \
#     POETRY_NO_INTERACTION=1

# WORKDIR /app

# COPY pyproject.toml poetry.lock ./

# RUN apt-get update && \
#     apt-get install -y gettext=${GETTEXT_VERSION} --no-install-recommends && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/* && \
#     pip install --no-cache-dir --upgrade pip==${PIP_VERSION} && \
#     pip install --no-cache-dir poetry==${POETRY_VERSION}

# COPY . .

# # due to https://github.com/python-poetry/poetry/issues/1382
# RUN poetry install --only main && \
#     poetry build && \
#     pip install --no-cache-dir dist/*.whl --no-deps && \
#     rm -rf dist/ && \
#     pip uninstall poetry -y

# RUN ln -s container.py quoter_app/settings/current.py && \
#     TESTING=TRUE ./manage.py compilemessages && \
#     TESTING=TRUE ./manage.py collectstatic --noinput

# CMD ["gunicorn", "quoter_app.wsgi", "-c", "gunicorn.py"]

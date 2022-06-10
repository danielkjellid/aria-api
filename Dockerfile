FROM python:3.10.2

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH /app/

# Add app user
RUN addgroup --system aria && adduser --system --group aria

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    bash-completion \
    less \
    lsof \
    vim \
    curl \
    postgresql-client \
    awscli \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache poetry

# Set app user and working directory
USER aria
WORKDIR /app

COPY --chown=aria poetry.lock pyproject.toml poetry.toml manage.py .env.test setup.cfg /app/
RUN poetry install --no-root --no-dev --no-interaction --no-ansi

# Copy application files
COPY --chown=aria aria/ /app/aria/

# Collect static files
RUN poetry run python manage.py collectstatic --noinput

COPY --chown=aria docker-entrypoint.sh /app
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
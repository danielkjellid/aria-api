FROM python:3.10.2

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH /app/

# Add app user
RUN groupadd -r aria && useradd --create-home aria -g aria

# Get postgresql-14 package manually, as the official package version only supports
# postgresql-13. These three lines can be removed once the official package is updated.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y lsb-release
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    bash-completion \
    less \
    lsof \
    vim \
    curl \
    postgresql-14 \
    awscli \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache poetry==1.2.0

# Set app user and working directory
USER aria
WORKDIR /app

COPY --chown=aria poetry.lock pyproject.toml poetry.toml manage.py .env.test setup.cfg /app/
RUN poetry install --no-root --no-dev --no-interaction --no-ansi

# Render needs a .ssh folder to make ssh tunneling work.
RUN mkdir ./.ssh && chmod 700 ./.ssh

# Copy application files
COPY --chown=aria aria/ /app/aria/
COPY --chown=aria public/ /app/public/
COPY --chown=aria bin/ /app/bin/

# Collect static files
RUN poetry run python manage.py collectstatic --noinput

COPY --chown=aria docker-entrypoint.sh /app
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
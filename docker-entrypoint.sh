#!/bin/bash
set -e

if [ "$1" = 'python' ]; then
    exec poetry run python ${*:2}
fi

if [ "$1" == "celery" ]; then
    exec poetry run celery -A aria worker -Q ${*:2} --concurrency=4 --loglevel=DEBUG
fi

if [ "$1" = 'gunicorn' ]; then
    exec poetry run gunicorn aria.wsgi:application ${*:2}
fi

if [ "$1" = 'migrate' ]; then
    exec poetry run python manage.py migrate ${*:2}
fi

if [ "$1" = 'shell' ]; then
    exec poetry run python manage.py shell ${*:2}
fi

if [ "$1" = 'shell_plus' ]; then
    exec poetry run python manage.py shell_plus ${*:2}
fi

if [ "$1" = 'dbshell' ]; then
    exec poetry run python manage.py dbshell ${*:2}
fi

if [ "$1" = 'db_dump' ]; then
    exec poetry run ./bin/db-dump ${*:2}
fi

exec "$@"
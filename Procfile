release: python3 manage.py migrate
web: newrelic-admin run-program gunicorn backend.wsgi --preload --log-file -
#!/usr/bin/env bash

set -o errexit
set -o pipefail

function postgres_ready(){
python3 << END
import sys
import psycopg2
import os

try:
    dbname = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST')
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=5432)
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

wait_for_db() {
    until postgres_ready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done
}


if [ "$1" == "server" ]; then
    wait_for_db
    echo "Running migrations"
    python3 manage.py migrate
    echo "Running collectstatic"
    python3 manage.py collectstatic --noinput
    exec gunicorn backend.wsgi -w 4 --worker-class gevent -b 0.0.0.0:8000 --chdir=/app
fi

if [ "$1" == "debug_server" ]; then
    wait_for_db
    echo "Running migrations"
    python3 manage.py migrate
    echo "Running collectstatic"
    python3 manage.py collectstatic --noinput
    exec python3 manage.py runserver 0.0.0.0:8000
fi


if [ "$1" == "nomigrate" ]; then
    wait_for_db
    echo "Running collectstatic"
    python3 manage.py collectstatic --noinput
    exec gunicorn backend.wsgi -w 4 --worker-class gevent -b 0.0.0.0:8000 --chdir=/app
fi

if [ "$1" == "migrate" ]; then
    wait_for_db
    echo "Running migrations"
    exec python3 manage.py "$@"
fi

if [ "$1" == "makemigrations" ];then
    wait_for_db
    exec python3 manage.py "$@"
fi

if [ "$1" == "dramatiq_worker" ]; then
    wait_for_db
    exec python3 manage.py rundramatiq
fi

echo "No action was specified"
exit 1
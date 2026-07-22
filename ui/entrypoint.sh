#!/bin/sh

set -e

if [ -f db/db.sqlite3 ]; then
    DB=1
fi

python manage.py collectstatic --clear --no-input
python manage.py migrate
python manage.py initxray

if [ -z "$DB" ]; then
    python manage.py createsuperuser --no-input
fi

exec "$@"

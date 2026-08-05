#!/bin/sh

set -e

if [ -f db/db.sqlite3 ]; then
    DB=1
fi

python src/ui/manage.py collectstatic --clear --no-input
python src/ui/manage.py migrate
python src/ui/manage.py initxray

if [ -z "$DB" ]; then
    python src/ui/manage.py createsuperuser --no-input
fi

exec "$@"

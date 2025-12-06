#!/bin/bash
# backend/scripts/dev.sh

set -e

cleanup() {
    echo "Cleaning up..."
    kill $(jobs -p) 2>/dev/null
}

trap cleanup EXIT

echo "Waiting for database..."
python -c "
import time
import sys
import psycopg2

retries = 30
while retries > 0:
    try:
        psycopg2.connect(
            dbname='${POSTGRES_DB:-standard_rag}',
            user='${POSTGRES_USER:-postgres}',
            password='${POSTGRES_PASSWORD:-postgres}',
            host='postgres'
        )
        print('Database connection successful!')
        break
    except psycopg2.OperationalError:
        retries -= 1
        if retries == 0:
            print('Could not connect to database after 30 seconds')
            sys.exit(1)
        print('Waiting for database...')
        time.sleep(1)
"

echo "Running migrations..."
alembic upgrade head || exit 1

echo "Starting development server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-delay 0.25

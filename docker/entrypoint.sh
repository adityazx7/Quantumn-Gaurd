#!/bin/sh
set -e

echo "=== QuantumGuard QDS Container Initialization ==="

# Wait for PostgreSQL if configured
if [ -n "$DATABASE_URL" ]; then
    echo "Applying Alembic database migrations..."
    alembic upgrade head || {
        echo "Alembic migration failed, checking if retry needed..."
        sleep 2
        alembic upgrade head
    }
fi

echo "Migrations completed successfully. Starting application server..."
exec "$@"

#!/bin/sh
# entrypoint.sh
echo "Applying migrations..."
cd app/database && alembic upgrade head && cd ../..
echo "Migrations applied."

exec "$@"
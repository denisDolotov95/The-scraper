#!/bin/sh
# entrypoint.sh
echo "Applying migrations..."
cd src/database && alembic upgrade head && cd ../..
echo "Migrations applied."

exec "$@"
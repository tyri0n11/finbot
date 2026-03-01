set -e

echo "Ensuring database ${POSTGRES_DB} exists..."
psql --username "$POSTGRES_USER" --dbname "postgres" \
  -c "CREATE DATABASE \"${POSTGRES_DB}\" OWNER ${POSTGRES_USER}" \
  || echo "Database ${POSTGRES_DB} already exists, skipping."

set -e

echo "Ensuring database ${POSTGRES_DB} exists..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
   CREATE DATABASE "${POSTGRES_DB}" OWNER ${POSTGRES_USER};
EOSQL || echo "Database ${POSTGRES_DB} already exists"

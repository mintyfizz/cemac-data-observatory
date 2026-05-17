#!/bin/sh
set -eu

escaped_db=$(printf "%s" "$POSTGRES_DB" | sed 's/"/""/g')
escaped_password=$(printf "%s" "$METABASE_READER_PASSWORD" | sed "s/'/''/g")

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'metabase_reader') THEN
        CREATE ROLE metabase_reader WITH LOGIN PASSWORD '${escaped_password}';
    ELSE
        ALTER ROLE metabase_reader WITH LOGIN PASSWORD '${escaped_password}';
    END IF;
END
\$\$;

GRANT CONNECT ON DATABASE "${escaped_db}" TO metabase_reader;
GRANT USAGE ON SCHEMA marts TO metabase_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO metabase_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO metabase_reader;
SQL

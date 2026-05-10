-- Read-only role for Metabase. Created once at container init.
-- Metabase can query marts but cannot write or access raw/staging data.
CREATE ROLE metabase_reader WITH LOGIN PASSWORD 'metabase_local_only';

GRANT CONNECT ON DATABASE warehouse TO metabase_reader;
GRANT USAGE ON SCHEMA marts TO metabase_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO metabase_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO metabase_reader;

# ADR-001: Postgres over a cloud warehouse

**Date:** 2025-05-10  
**Status:** Accepted

## Context

The pipeline processes ~30 years of World Bank data across 8 countries and 10
indicators — roughly 2,000–3,000 rows at initial load, growing by a few hundred
rows per weekly run. The project also needed to stay fully local and free during
development, with no cloud account or billing required to clone and run it.

The obvious alternatives to Postgres were BigQuery, DuckDB, and Snowflake.

## Decision

Use **Postgres 16** (via Docker) as the warehouse.

## Reasoning

**Scale fit.** At this data volume, Postgres query times are sub-second with
basic indexes. The marginal performance advantage of a columnar store (DuckDB,
BigQuery) does not materialise until datasets are orders of magnitude larger.
Optimising for a problem that doesn't exist yet is the wrong trade-off for a
learning project.

**SQL parity.** Every SQL pattern used in this project — window functions,
CTEs, aggregations, `FILTER` clauses — is supported identically in Postgres
and in BigQuery/Snowflake. Switching engines later requires no SQL rewrites.

**Zero friction local setup.** Postgres runs in a Docker container with a
single `docker compose up -d`. No cloud account, no credentials to manage, no
billing surprises. Anyone can clone the repo and run it immediately.

**dbt native support.** `dbt-postgres` is the reference adapter. All dbt
documentation examples use Postgres, which reduces the chance of adapter-
specific gotchas during a learning project.

**Operational simplicity.** One container hosts both the raw landing zone and
the marts schema. Schema separation (`raw`, `staging`, `marts`) provides the
same logical layering a cloud warehouse would, without the operational overhead
of managing multiple services.

## Trade-offs accepted

- **No query engine scaling.** If the dataset grew to millions of rows,
  Postgres row-store performance would degrade faster than a columnar engine.
  The right response at that point is a migration to DuckDB or BigQuery, not
  a premature architecture change now.

- **No built-in time-travel or zero-copy cloning.** Snowflake and BigQuery
  offer these natively. dbt snapshots cover the history-tracking use case at
  this scale.

- **Single-node.** Postgres on Docker is not horizontally scalable. Acceptable
  for a local analytical pipeline; a production deployment would add replicas
  or move to a managed service.

## Consequences

The marts schema is written as standard ANSI SQL with minor Postgres-isms
(`timestamptz`, `pg_isready`). Migrating to another Postgres-compatible engine
(e.g. Cloud SQL, Supabase, AlloyDB) is a config change. Migrating to a
columnar engine would require reviewing any Postgres-specific types and
confirming adapter support in dbt.

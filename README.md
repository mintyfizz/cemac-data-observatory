# CEMAC Data Observatory

A completed reference implementation of a local data platform for tracking digital development indicators across CEMAC countries, benchmarked against Rwanda and Kenya.

![Dashboard](docs/screenshots/dashboard.png)

## Project status

✅ Complete. This repository is kept as a finished, reproducible reference project.

## What this project does

- Extracts 10 World Bank indicators across 8 countries.
- Loads data into Postgres with idempotent upserts.
- Transforms data with dbt into analytics-ready marts.
- Orchestrates extraction + transformation with Prefect.
- Serves dashboards with Metabase.

## Stack

| Layer | Tool |
|---|---|
| Source | World Bank Open Data API |
| Extraction | Python (`requests`, `psycopg`) |
| Warehouse | Postgres 16 |
| Transformations | dbt |
| Orchestration | Prefect 3 |
| Dashboard | Metabase |
| Local environment | Docker Compose |

## Quick start

### Requirements

- Docker
- Python 3.11+
- ~2 GB free disk space

### 1) Clone and install

```bash
git clone <repo-url>
cd cemac-data-observatory
cp .env.example .env

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) Start local services

```bash
docker compose up -d
```

### 3) Configure Prefect (once)

```bash
set -a; source .env; set +a
prefect config set PREFECT_API_URL=http://localhost:4200/api
prefect concurrency-limit create world-bank 4
```

### 4) Run the pipeline

```bash
python -m flows.digital_readiness
```

## Local services

| Service | URL |
|---|---|
| Metabase | http://localhost:3000 |
| Prefect UI | http://localhost:4200 |
| pgAdmin | http://127.0.0.1:5051 |
| Postgres (from host machine) | `localhost:15432` |

Default local credentials:

- Postgres: `admin` / `admin`
- pgAdmin: `nathangatse@outlook.com` / `admin`

## Metabase first-run database connection

When Metabase asks to connect to a database, use:

| Field | Value |
|---|---|
| Host | `postgres` |
| Port | `5432` |
| Database | `warehouse` |
| Username | `metabase_reader` |
| Password | `metabase_local_only` |

The read-only role is created by `sql/init/02_metabase_reader.sql` and is limited to the `marts` schema.

## Running and scheduling

Manual run:

```bash
set -a; source .env; set +a
python -m flows.digital_readiness
```

Weekly schedule (keep process running):

```bash
python -m flows.serve
```

## dbt usage

dbt reads credentials from `~/.dbt/profiles.yml` (not from environment variables in this repo).

Use `dbt_project/profiles.yml.example` as your template.

```bash
cd dbt_project
dbt debug
dbt build
dbt docs generate && dbt docs serve
```

![dbt lineage graph](docs/screenshots/dbt-lineage.png)

## Data model (high level)

- `raw.observations`: landing table for extracted API data.
- `staging.stg_*`: cleaned and typed staging models.
- `marts.dim_countries`, `marts.dim_indicators`: dimensions.
- `marts.fct_observations`: main fact table.
- `marts.cemac_digital_readiness`: dashboard-ready wide table.
- `marts.mart_pipeline_health`: freshness/coverage summary.

## Repository layout

- `extract/`: World Bank extraction and loading logic
- `flows/`: Prefect orchestration
- `dbt_project/`: dbt models, tests, and docs
- `sql/init/`: Postgres initialization scripts
- `docs/`: architecture and design documentation
- `docker-compose.yml`: local stack definition

## Stop the stack

```bash
docker compose down
```

Remove volumes too:

```bash
docker compose down -v
```

## Design note

See [ADR-001](docs/decisions/ADR-001-postgres-over-cloud-warehouse.md) for the Postgres decision rationale.

## License

MIT — see [LICENSE](LICENSE).

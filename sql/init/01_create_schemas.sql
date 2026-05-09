-- raw: for landing data as-is from the source (World Bank API)
-- staging: for cleaned and transformed data ready for analysis
-- marts: for curated datasets optimized for specific analyses or dashboards
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE IF NOT EXISTS raw.observations (
    country_code   text NOT NULL,
    indicator_code text NOT NULL,
    year           integer NOT NULL,
    value          numeric,
    unit           text,
    obs_status     text,
    decimal_places integer,
    loaded_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (country_code, indicator_code, year)
);

CREATE INDEX IF NOT EXISTS idx_raw_obs_country   ON raw.observations(country_code);
CREATE INDEX IF NOT EXISTS idx_raw_obs_indicator ON raw.observations(indicator_code);
CREATE INDEX IF NOT EXISTS idx_raw_obs_year      ON raw.observations(year);

COMMENT ON TABLE raw.observations IS
  'Raw landing zone for World Bank observations. Idempotent on (country_code, indicator_code, year).';

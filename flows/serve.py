"""Register the pipeline with a weekly schedule and serve it."""
from __future__ import annotations

from prefect.client.schemas.schedules import CronSchedule

from flows.digital_readiness import digital_readiness_pipeline


if __name__ == "__main__":
    digital_readiness_pipeline.serve(
        name="weekly-digital-readiness",
        schedule=CronSchedule(cron="0 6 * * 1", timezone="Europe/Brussels"),
        tags=["weekly", "etl"],
        description="Weekly refresh of CEMAC digital readiness data from the World Bank API.",
        pause_on_shutdown=False,
    )

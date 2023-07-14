from datetime import datetime

from airflow import models
from airflow.providers.trino.operators.trino import TrinoOperator

with models.DAG(
        dag_id="refresh-freibe",
        schedule="*/1 * * * *",
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["datenplatform", "roxy"],
) as dag:
    trino_insert = TrinoOperator(
        task_id="trino_insert",
        sql=f"""
insert into lakehouse.platform.freibe_history
select
	id,
	now(),
	fuel_level,
	vehicle_type_id,
	latitude,
	longitude
from staging.platform.freibe
        """,
        handler=list,
    )
    (
            trino_insert
    )

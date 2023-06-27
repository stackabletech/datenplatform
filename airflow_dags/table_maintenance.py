from __future__ import annotations

from datetime import datetime

from airflow import models
from airflow.providers.trino.operators.trino import TrinoOperator

with models.DAG(
        dag_id="table-maintenance",
        schedule="0 * * * *",
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["datenplatform", "maintenance"],
) as dag:
    trino_maintenance = TrinoOperator(
        task_id="trino_maintenance",
        sql=f"""alter table lakehouse.smart_city.bikes_history execute optimize
        alter table lakehouse.smart_city.bikes_history execute expire_snapshots(retention_threshold => '7d')
        alter table lakehouse.smart_city.parking_garages_history execute optimize
        alter table lakehouse.smart_city.parking_garages_history execute expire_snapshots(retention_threshold => '7d')
        alter table lakehouse.smart_city.roxy_history execute optimize
        alter table lakehouse.smart_city.roxy_history execute expire_snapshots(retention_threshold => '7d')
        alter table lakehouse.smart_city.yoio_history execute optimize
        alter table lakehouse.smart_city.yoio_history execute expire_snapshots(retention_threshold => '7d')""",
        handler=list,
    )

    SCHEMA = "hive.cities"
    TABLE = "city"
    TABLE1 = "city1"
    TABLE2 = "city2"
    trino_multiple_queries = TrinoOperator(
        task_id="trino_multiple_queries",
        sql=f"""CREATE TABLE IF NOT EXISTS {SCHEMA}.{TABLE1}(cityid bigint,cityname varchar)
        INSERT INTO {SCHEMA}.{TABLE1} VALUES (2, 'San Jose')
        CREATE TABLE IF NOT EXISTS {SCHEMA}.{TABLE2}(cityid bigint,cityname varchar)
        INSERT INTO {SCHEMA}.{TABLE2} VALUES (3, 'San Diego')""",
        handler=list,
    )
    (
            trino_multiple_queries
    )

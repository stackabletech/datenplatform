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
    tables = [
        "lakehouse.platform.bikes_history",
        "lakehouse.platform.parking_garages_history",
        "lakehouse.platform.roxy_history",
        "lakehouse.platform.yoio_history",
    ]
    for table in tables:
        TrinoOperator(
            task_id=f"trino_maintenance_optimize_{table}",
            sql=f"alter table {table} execute optimize",
            handler=list,
        )
        TrinoOperator(
            task_id=f"trino_maintenance_expire_snapshots_{table}",
            sql=f"alter table {table} execute expire_snapshots(retention_threshold => '7d')",
            handler=list,
        )

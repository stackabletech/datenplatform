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
        sql=f"""alter table lakehouse.smart_city.bikes_history execute optimize;
alter table lakehouse.smart_city.bikes_history execute expire_snapshots(retention_threshold => '7d');
alter table lakehouse.smart_city.parking_garages_history execute optimize;
alter table lakehouse.smart_city.parking_garages_history execute expire_snapshots(retention_threshold => '7d');
alter table lakehouse.smart_city.roxy_history execute optimize;
alter table lakehouse.smart_city.roxy_history execute expire_snapshots(retention_threshold => '7d');
alter table lakehouse.smart_city.yoio_history execute optimize;
alter table lakehouse.smart_city.yoio_history execute expire_snapshots(retention_threshold => '7d');""",
        handler=list,
    )
    (
            trino_maintenance
    )

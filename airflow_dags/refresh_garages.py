from datetime import datetime

from airflow import models
from airflow.providers.trino.operators.trino import TrinoOperator

with models.DAG(
        dag_id="refresh-garages",
        schedule="*/5 * * * *",
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["datenplatform", "yoio"],
) as dag:
    trino_insert = TrinoOperator(
        task_id="trino_insert",
        sql=f"""
merge into lakehouse.platform.parking_garages_history as t
using (select * from staging.platform.parking_garages) as u
on u.obs_id = t.obs_id
when not matched then insert values (u.obs_id, u.obs_parkid, u.obs_state, u.obs_max, u.obs_free, u.obs_ts, u.park_name, u.park_id, u.trend, u.prozent, u.park_url, u.park_zone, u.free_color, u.status, u.latitude, u.longitude)
""",
        handler=list,
    )
    (
        trino_insert
    )

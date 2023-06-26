#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Example DAG using TrinoOperator.
"""
from __future__ import annotations

from datetime import datetime

from airflow import models
from airflow.providers.trino.operators.trino import TrinoOperator


with models.DAG(
        dag_id="refresh-yoio",
        schedule="*/5 * * * *",
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["datenplatform", "yoio"],
) as dag:
    trino_insert = TrinoOperator(
        task_id="trino_insert",
        sql=f"""merge into lakehouse.smart_city.parking_garages_history as t
using
  (select * from staging.smart_city.parking_garages) as u
on u.obs_id = t.obs_id
when not matched then insert values (u.obs_id, u.obs_parkid, u.obs_state, u.obs_max, u.obs_free, u.obs_ts, u.park_name, u.park_id, u.trend, u.prozent, u.park_url, u.park_zone, u.free_color, u.status, u.latitude, u.longitude)""",
        handler=list,
    )
    (
            trino_insert
    )

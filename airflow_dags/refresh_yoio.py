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
        sql=f"""insert
	into
	lakehouse.platform.yoio_history
	select
		current_timestamp(6) as timestamp,
		nr,
		current_range_meters,
		rental_uri_android,
		rental_uri_ios,
		rental_uri_web,
		latitude,
		longitude
from
		staging.platform.yoio""",
        handler=list,
    )
    (
            trino_insert
    )

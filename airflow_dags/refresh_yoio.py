with models.DAG(
        dag_id="refresh-yoio",
        schedule="@once",  # Override to match your needs
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["datenplatform", "yoio"],
) as dag:
    trino_insert = TrinoOperator(
        task_id="trino_insert",
        sql=f"""INSERT INTO {SCHEMA}.{TABLE} VALUES (1, 'San Francisco');""",
        handler=list,
    )
    (
            trino_insert
    )
# coding: utf-8
import json
import os

import urllib3
from sqlalchemy import create_engine
from sqlalchemy.sql import expression
from trino.sqlalchemy import URL

import trino_connection

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_sql():
    engine = trino_connection.get_trino_engine()

    with engine.connect() as connection:
        type_dict = {}

        for file_name in os.listdir('sql'):
            name = os.path.basename(file_name).split('.')[0]

        try:
            res = connection.execute(expression.text(f"select * from staging.smart_city.{name}"))
            for row in res:
                geo_type = json.loads(row[-1])['type']
                content = type_dict.get(geo_type, [])
                content.append(file_name)
                type_dict[geo_type] = sorted(content)
                break
        except Exception as e:
            print(file_name, e)

        print(type_dict)
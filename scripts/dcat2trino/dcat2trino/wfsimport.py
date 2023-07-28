from owslib.wfs import WebFeatureService
import ast
from io import StringIO

import geopandas as gpd
import pandas as pd
import requests
from sqlalchemy.sql import expression
import util
import trino_connection

def import_wfs(base_url, endpoints):
    for endpoint in endpoints:
        wfsUrl = base_url + '/' + endpoint
        wfs = WebFeatureService(url=wfsUrl, version="2.0.0")
        for featureType in list(wfs.contents):
            url = f"{wfsUrl}/{featureType}"

            r = requests.get(url)
            content = StringIO(r.content.decode('utf-8'))
            df_new = pd.DataFrame()
            geom_type = ""

            try:
                gdf = gpd.read_file(content)
                geom_type = str(gdf.geometry.geom_type[0])
                df = pd.DataFrame(gdf)
                for col in df.columns:
                    try:
                        df[col] = df[col].apply(ast.literal_eval)
                        s = df[col].explode()
                        if len(s.apply(pd.Series).columns) > 1:
                            s = pd.concat([s, s.apply(pd.Series)], axis=1).drop(col, axis=1)
                            s = s.reset_index()
                            df_new = df_new.merge(s, how='left', left_on=df_new.index, right_on='index')
                        else:
                            df_new[col] = df[col]
                    except Exception as e:
                        df_new[col] = df[col]
            except pd.errors.ParserError:
                print(url, 'Parse Error CSV')

            description_1 = url.split('?')[0].split('/')[-1]
            description_2 = url.split('typename=ms:')[-1].split('&')[0].replace('-', '_')
            sqlfile = f"sql/{description_1}_{description_2}.sql"

            engine = trino_connection.get_trino_engine()
            with open(sqlfile, 'w') as writer:
                with engine.connect() as connection:
                    statement = f"create or REPLACE view staging.smart_city.{description_1}_{description_2} as\n"
                    statement += "\twith json as (\n"
                    statement += "\t\tselect\n"
                    statement += "\t\tcast(\n"
                    statement += "\t\tjson_parse(\n"
                    statement += "\t\tjson_query(data,\n"
                    statement += "\t\t'lax $.features[*]' with array WRAPPER)) as array(row(\n"
                    statement += "\t\t\tproperties row(\n"
                    sts = []
                    for column in df_new.columns:
                        if column != 'geometry':
                            sts.append(
                                f"\t\t\t\t{util.cleanup_name(column)} {util.typemapping.get(str(df_new.dtypes[column]), 'varchar')}")
                    statement += ",\n".join(sts)
                    statement += "\n"
                    statement += "\t\t\t),\n"
                    statement += "\t\t\tgeometry row(\n"
                    statement += "\t\t\t\ttype varchar,\n"
                    if geom_type in ('Polygon', 'MultiLineString'):
                        statement += "\t\t\t\tcoordinates array(array(array(double)))\n"
                    elif geom_type == 'Point':
                        statement += "\t\t\t\tcoordinates array(double)\n"
                    elif geom_type == 'LineString':
                        statement += "\t\t\t\tcoordinates array(array(double))\n"
                    elif geom_type == 'MultiPolygon':
                        statement += "\t\t\t\tcoordinates array(array(array(array(double))))\n"

                    statement += "\t\t)))) temp\n"
                    statement += f"from storage.raw.\"{url}\")\n"
                    statement += "select\n"

                    sts = []
                    for column in df_new.columns:
                        if column != 'geometry':
                            sts.append(f"\tproperties.{util.cleanup_name(column)} {util.cleanup_name(column)}")

                    statement += ",\n".join(sts)
                    statement += ",\n"
                    statement += "\tto_geometry(from_geojson_geometry(json_format(cast(geometry as json)))) as geometry,\n"
                    statement += "\tjson_format(cast(geometry as json)) as geometry_geojson,\n"
                    statement += f"\tjson_object(\'type\': \'{geom_type}\', \'geometry\': json_format(cast(geometry as json)) FORMAT JSON) as geometry_geojson2\n"
                    statement += "from (json cross join unnest(temp))"
                    writer.write(statement)

                    try:
                        #connection.execute(expression.text(statement))
                        print("skipping trino part")
                    except Exception as e:
                        print(f"Failed to create table [{description_1}_{description_2}] due to [{e}]")
                        continue

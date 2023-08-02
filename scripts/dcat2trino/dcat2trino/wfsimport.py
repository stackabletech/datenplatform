import ast
from io import StringIO

import fiona
import geopandas as gpd
import pandas as pd
import pyogrio
import requests
from owslib.wfs import WebFeatureService
from sqlalchemy.sql import expression

import trino_connection
import util


class WFSImporter(object):

    def __init__(self, base_url, end_points):
        self._base_url = base_url
        self._end_points = end_points
        self._dtypes_dict = dict()

    def import_wfs(self):
        for endpoint in self._end_points:
            wfsUrl = self._base_url + '/' + endpoint
            wfs = WebFeatureService(url=wfsUrl, version="2.0.0")
            for featureType in list(wfs.contents):
                url = f"{wfsUrl}?request=getfeature&service=wfs&version=2.0.0&typename={featureType}&outputformat=geojson&srsname=urn:ogc:def:crs:EPSG::4326"
                print(f"Retrieving {url}")

                r = requests.get(url)
                content = StringIO(r.content.decode('utf-8'))
                # geom_type = ""
                # df = pd.DataFrame()
                self._dtypes_dict = dict()

                try:
                    gdf = gpd.read_file(content)
                    geom_type = str(gdf.geometry.geom_type[0])
                    df = pd.DataFrame(gdf)
                    self._dtypes_dict.update(df.dtypes.apply(lambda x: x.name).to_dict())
                except (pd.errors.ParserError, KeyError, pyogrio.errors.DataSourceError, fiona.errors.DriverError) as e:
                    print(url, e)
                    continue

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
                        for column in df.columns:
                            if column != 'geometry':
                                sts.append(self._create_json_rows(df[column], column, n_tabs=4))
                        statement += ",\n".join(sts)
                        statement += "\n"
                        statement += "\t\t\t),\n"
                        statement += "\t\t\tgeometry row(\n"
                        statement += "\t\t\t\ttype varchar,\n"
                        if geom_type == 'Polygon':
                            statement += "\t\t\t\tcoordinates array(array(array(double)))\n"
                        elif geom_type == 'Point':
                            statement += "\t\t\t\tcoordinates array(double)\n"
                        elif geom_type == 'LineString':
                            statement += "\t\t\t\tcoordinates array(array(double))\n"
                        elif geom_type == 'MultiPolygon':
                            statement += "\t\t\t\tcoordinates array(array(array(array(double))))\n"
                        elif geom_type == 'MultiLineString':
                            statement += "\t\t\t\tcoordinates flatten(array(array(array(double))))\n"
                            geom_type = 'LineString'

                        statement += "\t\t)))) temp\n"
                        statement += f"from storage.raw.\"{url}\")\n"
                        statement += "select\n"

                        sts = []
                        for column in df.columns:
                            if column != 'geometry':
                                sts.append(self._create_output(df[column], column, 'properties'))

                        statement += ",\n".join(sts)
                        statement += ",\n"
                        statement += "\tto_geometry(from_geojson_geometry(json_format(cast(geometry as json)))) as geometry,\n"
                        statement += "\tjson_format(cast(geometry as json)) as geometry_geojson,\n"
                        statement += f"\tjson_object(\'type\': \'{geom_type}\', \'geometry\': json_format(cast(geometry as json)) FORMAT JSON) as geometry_geojson2\n"
                        statement += "from (json \n"
                        sts = ["\tcross join unnest(temp)"]
                        sts = self._create_nested_join(df, sts)
                        statement += "\n".join(sts)
                        statement += "\n)"
                        writer.write(statement)

                        try:
                            connection.execute(expression.text(statement))
                        except Exception as e:
                            print(f"Failed to create table [{description_1}_{description_2}] due to [{e}]")
                            continue

    def _create_json_rows(self, s_t, col_t, n_tabs=4):
        tabs = n_tabs * '\t'
        try:
            s = s_t.apply(ast.literal_eval)
            s = s.explode()
            if s.shape[0] != s_t.shape[0]:
                if len(s.apply(pd.Series).columns) > 1:
                    nested_entry = f"{tabs}{col_t} array(row(\n"
                    sub_entries = []
                    s = pd.concat([s, s.apply(pd.Series)], axis=1).drop(col_t, axis=1)
                    s = s.reset_index()
                    s.drop('index', axis=1, inplace=True)
                    self._dtypes_dict.update(s.dtypes.apply(lambda x: x.name).to_dict())
                    for c in s.columns:
                        sub_entries.append(self._create_json_rows(s[c].astype(str), c, n_tabs=n_tabs+1))

                    nested_entry += ",\n".join(sub_entries)
                    nested_entry += "))"
                    return nested_entry
                else:
                    return f"{tabs}{col_t} array(varchar)"
            else:
                return f"{tabs}{util.cleanup_name(col_t)} {util.typemapping.get(str(self._dtypes_dict[col_t]), 'varchar')}"
        except Exception as e:
            return f"{tabs}{util.cleanup_name(col_t)} {util.typemapping.get(str(self._dtypes_dict[col_t]), 'varchar')}"

    def _create_output(self, s_t, col_t, root_t):
        if root_t != 'properties':
            pre = root_t + '_'
        else:
            pre = ''
        try:
            s = s_t.apply(ast.literal_eval)
            s = s.explode()
            if s.shape[0] != s_t.shape[0]:
                if len(s.apply(pd.Series).columns) > 1:
                    sub_entries = []
                    s = pd.concat([s, s.apply(pd.Series)], axis=1).drop(col_t, axis=1)
                    s = s.reset_index()
                    s.drop('index', axis=1, inplace=True)
                    for c in s.columns:
                        sub_entries.append(self._create_output(s[c].astype(str), c, root_t=col_t))

                    return ",\n".join(sub_entries)
                else:
                    return f"\t{root_t}.{util.cleanup_name(col_t)} {pre}{util.cleanup_name(col_t)}"
            else:
                return f"\t{root_t}.{util.cleanup_name(col_t)} {pre}{util.cleanup_name(col_t)}"
        except Exception as e:
            return f"\t{root_t}.{util.cleanup_name(col_t)} {pre}{util.cleanup_name(col_t)}"

    def _create_nested_join(self, df_t, entries_t, root_t='properties'):
        entries = entries_t
        for col_t in df_t.columns:
            s_t = df_t[col_t]
            try:
                s = s_t.apply(ast.literal_eval)
                s = s.explode()
                if len(s.apply(pd.Series).columns) > 1:
                    s = pd.concat([s, s.apply(pd.Series)], axis=1).drop(col_t, axis=1)
                    s = s.reset_index()
                    s.drop('index', axis=1, inplace=True)
                    entries.append(f"\tcross join unnest({root_t}.{col_t}) as {col_t}")
                    entries = self._create_nested_join(s.astype(str), entries, root_t=col_t)
            except:
                pass
        return entries

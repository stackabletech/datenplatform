import os
import urllib.request

import pandas as pd
from rdflib import Graph
from sqlalchemy import text

import trino_connection
import util
import ssl


def import_dcat(url):
    # Define the SPARQL query to extract datasets provided by "Stadt Freiburg"
    sparql_query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?dataset ?distribution ?description ?downloadurl ?modified ?format
        WHERE {
            ?dataset a dcat:Dataset .
            ?dataset dcat:distribution ?distribution .
            ?distribution dct:description ?description .
            ?distribution dcat:downloadURL ?downloadurl .
            ?distribution dct:modified ?modified .
            ?distribution dct:format ?format .
            
        }
    """
    ssl._create_default_https_context = ssl._create_unverified_context

    # Load RDF data from the URL
    graph = Graph()
    graph.parse(url)

    qres = graph.query(sparql_query)
    for row in qres:
        print(f"Processing dataset [{row.dataset}]")
        if str(row.format) != "http://publications.europa.eu/resource/authority/file-type/CSV":
            print(f"skipping record, not csv: {row.format}")
            continue

        datafile = f"work/{util.cleanup_name(row.description)}.csv"
        sqlfile = f"sql/{util.cleanup_name(row.description)}.sql"

        if os.path.isfile(datafile):
            print(f"file has already been downloaded")
        else:
            print(f"downloading dataset from {row.downloadurl}...")
            try:
                urllib.request.urlretrieve(row.downloadurl, datafile)
            except urllib.error.HTTPError as e:
                print(f"Download failed: [{e}]")
                continue

        print(f"analyzing csv structure ..")
        separator = ','
        try:
            df = pd.read_csv(datafile, decimal=',', sep=separator)
        except pd.errors.ParserError as e:
            print(f"Failed to parse {datafile} falling back to ; as separator and trying again..")
            try:
                separator = ';'
                df = pd.read_csv(datafile, decimal=',', sep=separator)
            except pd.errors.ParserError as e:
                print(f"Failed to parse {datafile} with ; as separator, giving up!")
                continue

        print(f"Finished parsing [{datafile}], identified [{separator}] as separator")

        engine = trino_connection.get_trino_engine()

        with open(sqlfile, 'w') as writer:
            with engine.connect() as connection:
                statement = f"CREATE or REPLACE VIEW staging.smart_city.{util.cleanup_name(row.description)} AS\n"
                statement += f"WITH temp AS (SELECT *\n"
                statement += f"\tFROM storage.csv.\"{row.downloadurl}\")\n"
                statement += f"SELECT\n"
                for column in range(len(df.columns)):
                    statement += f"\tCAST(trim(LEADING '\"' FROM trim(TRAILING '\"' FROM \"{df.columns[column]}\")) AS {util.typemapping[str(df.dtypes[column])]}) {util.cleanup_name(df.columns[column])}"
                    if column < len(df.columns) - 1:
                        statement += ",\n"
                    else:
                        statement += "\n"
                statement += f"FROM temp\n"
                writer.write(statement + ";")

                try:
                    connection.execute(text(statement))
                except Exception as e:
                    print(f"Failed to create table [{util.cleanup_name(row.description)}] due to [{e}]")
                    continue
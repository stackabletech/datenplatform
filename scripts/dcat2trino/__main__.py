from rdflib import Graph
import urllib.request
import os
import pandas as pd
from sqlalchemy import create_engine
from trino.sqlalchemy import URL
from sqlalchemy.sql.expression import select, text

urllib.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cleanup_name(name):
    return str(name) \
        .replace(" ", "_") \
        .replace("(", "") \
        .replace(")", "") \
        .replace("-", "_") \
        .replace(",", "") \
        .replace(".", "") \
        .replace("\\", "") \
        .replace("/", "") \
        .lower() \
        .replace("ä", "ae") \
        .replace("ü", "ue") \
        .replace("ö", "oe") \
        .replace("ß", "ss")


typemapping = {"object": "varchar", "int64": "bigint", "float64": "double"}

# Define the RDF data URL
data_url = "https://fritz.freiburg.de/duva2dcat/dcat/catalog"

# Load RDF data from the URL
graph = Graph()
graph.parse(data_url)

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

engine = create_engine('trino://admin:***REMOVED***@85.215.223.118:31488/lakehouse')
engine = create_engine(
    URL(
        host="85.215.223.118",
        port=31488,
        catalog="lakehouse",
        user="admin",
        password="***REMOVED***"
    ),
    connect_args={
        "verify": False
    }
)
connection = engine.connect()

qres = graph.query(sparql_query)
for row in qres:
    print(f"Processing dataset [{row.dataset}]")
    if str(row.format) != "http://publications.europa.eu/resource/authority/file-type/CSV":
        print(f"skipping record, not csv: {row.format}")
        continue

    datafile = f"work/{row.description}.csv"
    sqlfile = f"sql/{row.description}.sql"

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
        df = pd.read_csv(datafile, decimal=',')
    except pd.errors.ParserError as e:
        print(f"Failed to parse {datafile} falling back to ; as separator and trying again..")
        try:
            df = pd.read_csv(datafile, decimal=',', sep=";")
            separator = ';'
        except pd.errors.ParserError as e:
            print(f"Failed to parse {datafile} with ; as separator, giving up!")
            continue

    print(f"Finished parsing [{datafile}], identified [{separator}] as separator")

    with open(sqlfile, 'w') as writer:
        statement = f"CREATE or REPLACE VIEW staging.smart_city.{cleanup_name(row.description)} AS\n"
        statement += f"WITH temp AS (SELECT *\n"
        statement += f"\tFROM storage.csv.\"{row.downloadurl}\")\n"
        statement += f"SELECT\n"
        for column in range(len(df.columns)):
            statement +=  f"\tCAST(trim(LEADING '\"' FROM trim(TRAILING '\"' FROM \"{df.columns[column]}\")) AS {typemapping[str(df.dtypes[column])]}) {cleanup_name(df.columns[column])}"
            if column < len(df.columns) - 1:
                statement += ",\n"
            else:
                statement += "\n"
        statement += f"FROM temp\n"
        writer.write(statement, ";")

        try:
            connection.execute(text(statement))
        except Exception as e:
            print(f"Failed to create table [{cleanup_name(row.description)}] due to [{e}]")
            continue

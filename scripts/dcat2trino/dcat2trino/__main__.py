

import os
import pandas as pd
from sqlalchemy import create_engine
from trino.sqlalchemy import URL
from sqlalchemy.sql.expression import select, text
import json

import wfsimport
import dcatimport

#urllib.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    sources_file_path = os.path.abspath("../../../source_definitions/sources.json")

    # Load definitions of sources to import from definition file
    # TODO: Move hard coded file path to a command line parameter
    with open(sources_file_path) as sources_file:
        try:
            sources_json = json.loads(sources_file.read())
        except Exception as e:
            print(f"Failed to parse sources config from {sources_file_path} due to:  [{e}]")
            exit(1)

    # Import all defined wfs endpoints
    for service in sources_json["wfs"]:
        # Do some basic integrity checking and skip import if they fail

        # We need a base_url
        base_url = service["base_url"]
        if base_url is None:
            print(f"base_url not set for service of type wfs, skipping...")
            continue

        # If no endpoints are defined there is nothing to do for us
        services = service["services"]
        if len(services) == 0:
            print(f"no endpoints defined for service at [{base_url}], skipping ...")
            continue

        wfsimport.import_wfs(base_url, services)


    # Import all defined dcat endpoints
    for service in sources_json["dcatap"]:
        dcatimport.import_dcat(service)

    print("done")

if __name__ == "__main__":
    main()
# DCAT-AP to Trino import tool

This is an early prototype of a tool that connects to a DCAT-AP endpoint, parses the available datasets and generates sql statements to create views in Trino that make these endpoints available as tables.


## Setup
Copy the file `trino_connection.py.template` to `trino_connection.py` and edit according to your needs.
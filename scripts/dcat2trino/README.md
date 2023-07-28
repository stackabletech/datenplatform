# DCAT-AP to Trino import tool

This is an early prototype of a tool that connects to a DCAT-AP endpoint, parses the available datasets and generates sql statements to create views in Trino that make these endpoints available as tables.



## Setup
### Trino Connection
Copy the file `dcat2trino/trino_connection.py.template` to `dcat2trino/trino_connection.py` and edit according to your needs.

### Dependency Management
The project uses [poetry](https://python-poetry.org/) for dependency management.
Just run `poetry run dcat2trino` in this directory, and it should retrieve everything automatically.


If you do not want to use this, the `pyproject.toml` file lists dependencies in required versions.
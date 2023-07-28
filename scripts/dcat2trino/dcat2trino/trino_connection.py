from sqlalchemy import create_engine
from trino.sqlalchemy import URL


def get_trino_engine():
    # load trino connection details from file
    # TODO: make this command line parameters
    import trino_configuration

    return create_engine(
        URL(
            host=trino_configuration.host,
            port=trino_configuration.port,
            catalog=trino_configuration.catalog,
            user=trino_configuration.user,
            password=trino_configuration.password
        ),
        connect_args={
            "verify": False
        }
    )

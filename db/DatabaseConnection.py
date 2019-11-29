import psycopg2

from db.config import config


class DatabaseConnection(object):
    """
    Handles the connection to the PostGreSQL database
    """

    def __init__(self):
        """
        Connects to the PostgreSQL database server
        """
        self._connection = None

        # read connection parameters
        params = config()

        # create connection to the PostgreSQL server
        self._connection = psycopg2.connect(**params)
        self._connection.autocommit = True  # persist changes to DB automatically

    def get_connection(self):
        """
        Accessor for the database connection
        :return: the newly created database connection
        """
        return self._connection

    def __del__(self):
        """
        Destructor to close the database connection
        :return: None
        """
        if self._connection is not None:
            self._connection.close()
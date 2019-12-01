from db.DatabaseConnection import DatabaseConnection
from db.config import config


def init_schemas():
    _get_postgres_version()
    _create_schemas()
    _initialize_team_parameters()


def _get_postgres_version():
    db = DatabaseConnection()

    with db.get_connection().cursor() as cursor:
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        print('PostgreSQL database version: ' + db_version[0])


def _create_schemas():
    print("Initializing schemas...")
    db = DatabaseConnection()
    connection = db.get_connection()

    with connection.cursor() as cursor:
        with open("db/sql/schemas.sql", "r") as f:
            sql = f.read()
            cursor.execute(sql)

    print("Schemas successfully created.")


def _initialize_team_parameters():
    print("Initializing team parameters...")
    db = DatabaseConnection()

    with db.get_connection().cursor() as cursor:
        cursor.execute("SELECT * FROM tms.team_parameters")
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO tms.team_parameters (max_team_size, min_team_size, are_parameters_set) "
                "VALUES (%s, %s, %s)",
                (0, 0, False))

    print("Parameters successfully initialized.")



import os
import sys

try:
    from db_connection import get_oracle_connection, get_sqlite_connection
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from db_connection import get_oracle_connection, get_sqlite_connection


def list_user_tables(oracle_conn=None):
    """
    List user-created tables in the Oracle database, excluding system tables.

    This function retrieves the list of tables created by the user, excluding
    system tables such as those prefixed with 'SYS_', 'LOGMNR', 'MVIEW', etc.

    :param oracle_conn: A valid connection to Oracle DB.
    """
    if not oracle_conn:
        oracle_conn = get_oracle_connection()
    cursor = oracle_conn.cursor()
    query = """
        SELECT table_name
        FROM user_tables
        WHERE table_name NOT LIKE 'SYS_%'
        AND table_name NOT LIKE 'LOGMNR%'
        AND table_name NOT LIKE 'MVIEW%'
        AND table_name NOT LIKE 'AQ$_%'
        AND table_name NOT LIKE 'LOGSTDBY%'
        AND table_name NOT LIKE 'ROLLING$%'
        AND table_name NOT LIKE 'REDO_%'
        AND table_name NOT LIKE 'SQLPLUS%'
        ORDER BY table_name
    """
    cursor.execute(query)
    tables = cursor.fetchall()

    print("User-created tables:")
    for table in tables:
        print(table[0])

    cursor.close()


def check_tables_exist(sqlite_conn=None):
    """
    Check the existence of tables in SQLite database.

    :param conn: SQLite connection object
    """
    if not sqlite_conn:
        sqlite_conn = get_sqlite_connection()
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in SQLite DB:", tables)


if __name__ == "__main__":
    check_tables_exist()
    # list_user_tables()

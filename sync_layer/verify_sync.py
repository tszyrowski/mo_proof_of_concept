import datetime
import os
import sys

import cx_Oracle
import sqlite3

try:
    from core_functionalities.app_logging import get_logger
    from sync_layer.db_connection import (
        get_oracle_connection,
        get_sqlite_connection,
    )
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core_functionalities.app_logging import get_logger
    from sync_layer.db_connection import (
        get_oracle_connection,
        get_sqlite_connection,
    )

logger = get_logger(__name__)


def verify_sync():
    """
    Verify that the data has been synchronized from SQLite to Oracle DB.
    """

    # Connect to Oracle
    try:
        oracle_conn = get_oracle_connection()
        oracle_cursor = oracle_conn.cursor()
        print("Connected to Oracle DB successfully.")
    except cx_Oracle.Error as e:
        print("Error connecting to Oracle DB:", e)
        return

    # Connect to SQLite
    try:
        sqlite_conn = get_sqlite_connection()
        sqlite_cursor = sqlite_conn.cursor()
        print("Connected to SQLite DB successfully.")
    except sqlite3.Error as e:
        print("Error connecting to SQLite DB:", e)
        return

    # Define tables to verify
    tables = {
        "sides": ["id", "side_name"],
        "questions": ["id", "side_id", "question"],
        "users": ["id", "username", "password"],
    }

    for table, columns in tables.items():
        # Fetch from SQLite
        sqlite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table}")
        sqlite_records = sqlite_cursor.fetchall()

        # Fetch from Oracle
        oracle_cursor.execute(f"SELECT {', '.join(columns)} FROM {table}")
        oracle_records = oracle_cursor.fetchall()

        # Compare
        if sqlite_records == oracle_records:
            print(f"Table '{table}' is synchronized correctly.")
        else:
            print(f"Table '{table}' synchronization mismatch.")
            print("SQLite Records:")
            for record in sqlite_records:
                print(record)
            print("Oracle Records:")
            for record in oracle_records:
                print(record)

    # Close connections
    oracle_cursor.close()
    oracle_conn.close()
    sqlite_conn.close()
    print("Verification completed.")


if __name__ == "__main__":
    verify_sync()

import datetime
import os
import sys

import cx_Oracle

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


def fetch_latest_records_sqlite(conn, table, last_sync_time):
    """
    Fetch records modified after the last sync time from SQLite.

    :param conn: SQLite connection object
    :param table: Table name to fetch records from
    :param last_sync_time: Datetime object representing the last sync time
    :return: List of tuples representing the records
    """
    cursor = conn.cursor()

    # Check if the updated_at column exists
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]

    if "updated_at" in columns:
        query = f"""
        SELECT * FROM {table}
        WHERE updated_at > ?
        """
        cursor.execute(query, (last_sync_time,))
    else:
        logger.warning(
            f"Table {table} does not have 'updated_at' column. "
            f"Fetching all records."
        )
        query = f"SELECT * FROM {table}"
        cursor.execute(query)

    return cursor.fetchall()


def sync_table_to_oracle(oracle_conn, table, columns, records):
    """
    Sync records from SQLite to Oracle DB for a specific table.

    :param oracle_conn: Oracle connection object
    :param table: Table name to sync
    :param columns: List of column names
    :param records: List of tuples representing the records
    """
    cursor = oracle_conn.cursor()

    cursor.execute(
        "SELECT user, sys_context('USERENV', 'CURRENT_SCHEMA') FROM dual"
    )
    result = cursor.fetchone()
    logger.info(
        f"Connected to Oracle as user: {result[0]}, schema: {result[1]}"
    )

    cursor.execute("SELECT sys_context('USERENV', 'CON_NAME') FROM dual")
    pdb_name = cursor.fetchone()
    logger.info(f"Connected to PDB: {pdb_name[0]}")

    # Explicitly specify the schema to avoid confusion
    schema = "SYSTEM"

    # Use fully qualified table names
    table_with_schema = f"{schema}.{table}"

    cursor.execute(
        "SELECT user, sys_context('USERENV', 'CURRENT_SCHEMA') FROM dual"
    )
    result = cursor.fetchone()
    logger.info(
        f"Connected to Oracle as user: {result[0]}, schema: {result[1]}"
    )

    # Assume first column is the primary key (id)
    primary_key = columns[0]
    non_primary_columns = columns[1:]

    # Columns for the merge statement, excluding the primary key
    merge_columns = ", ".join(
        [f"d.{col} = s.{col}" for col in non_primary_columns]
    )

    # MERGE statement to either update or insert records
    # NOTE it is different than POSTGRES `ON CONFLICT`
    merge_query = f"""
        MERGE INTO {table_with_schema} d
        USING (
            SELECT 
            {', '.join([f':{i+1} AS {col}' for i, col in enumerate(columns)])}
            FROM dual
        ) s
        ON (d.{primary_key} = s.{primary_key})
        WHEN MATCHED THEN
            UPDATE SET {merge_columns}
        WHEN NOT MATCHED THEN
            INSERT ({", ".join(columns)})
            VALUES ({", ".join([f"s.{col}" for col in columns])})
    """

    try:
        for record in records:
            # Ensure each record has the correct number of columns
            if len(record) != len(columns):
                raise ValueError(
                    f"Record {record} differ column count {len(columns)}"
                )

            cursor.execute(merge_query, record)
            logger.debug(f"MERGE query: {merge_query}")
            logger.debug(f"Record to insert/update: {record}")
        oracle_conn.commit()
        logger.info(
            f"Synced {len(records)} records to {table_with_schema} in Oracle."
        )
    except cx_Oracle.Error as e:
        logger.error(f"Error syncing records to {table_with_schema}: {e}")
        oracle_conn.rollback()  # Rollback in case of failure
        raise
    finally:
        cursor.close()


def get_last_sync_time(oracle_conn):
    """
    Retrieve the last synchronization time from the sync_metadata table.

    :param oracle_conn: Oracle connection object
    :return: Datetime object representing the last sync time
    """
    cursor = oracle_conn.cursor()
    cursor.execute("SELECT last_sync FROM sync_metadata WHERE sync_id = 1")
    result = cursor.fetchone()

    if result:
        return result[0]  # Return the last sync time as a datetime object
    else:
        # If no sync has occurred, return the epoch
        return datetime.datetime(1970, 1, 1)


def update_last_sync_time(oracle_conn, new_sync_time):
    """
    Update the last synchronization time in the sync_metadata table.

    :param oracle_conn: Oracle connection object
    :param new_sync_time: Datetime object representing the new sync time
    """
    cursor = oracle_conn.cursor()

    cursor.execute(
        """
        MERGE INTO sync_metadata d
        USING (SELECT 1 AS sync_id, :1 AS last_sync FROM dual) s
        ON (d.sync_id = s.sync_id)
        WHEN MATCHED THEN
            UPDATE SET d.last_sync = s.last_sync
        WHEN NOT MATCHED THEN
            INSERT (sync_id, last_sync)
            VALUES (s.sync_id, s.last_sync)
    """,
        (new_sync_time,),
    )

    oracle_conn.commit()


def sync_databases():
    """
    Perform synchronization from SQLite to Oracle DB.
    """
    # Connect to databases
    oracle_conn = get_oracle_connection()
    sqlite_conn = get_sqlite_connection()

    if not oracle_conn or not sqlite_conn:
        logger.error("Database connections failed. Exiting sync.")
        return

    # Define tables to sync and their columns
    tables = {
        "sides": ["id", "side_name"],
        "questions": ["id", "side_id", "question"],
        "users": ["id", "username", "password"],
    }

    last_sync_time = get_last_sync_time(oracle_conn)
    logger.info(f"Last sync time: {last_sync_time}")

    for table, columns in tables.items():
        records = fetch_latest_records_sqlite(
            sqlite_conn, table, last_sync_time
        )
        if records:
            sync_table_to_oracle(oracle_conn, table, columns, records)
        else:
            logger.info(f"No new records to sync for table {table}.")

    # Update the last sync time to now
    new_sync_time = datetime.datetime.now()
    update_last_sync_time(oracle_conn, new_sync_time)
    logger.info(f"Updated last sync time to: {new_sync_time}")

    # Close connections
    sqlite_conn.close()
    oracle_conn.close()
    logger.info("Synchronization completed and connections closed.")


if __name__ == "__main__":
    sync_databases()

import os
import sqlite3
import sys

import cx_Oracle
from dotenv import load_dotenv

try:
    from core_functionalities.app_logging import get_logger
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core_functionalities.app_logging import get_logger

logger = get_logger(__name__)


def load_environment():
    """
    Load environment variables from .env or system environment if not set.

    Raises:
        FileNotFoundError: If the .env file is not found and no environment
                           variables are set.
    """
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    if not all(
        var in os.environ
        for var in [
            "ORACLE_USER",
            "ORACLE_PASSWORD",
            "ORACLE_HOST",
            "ORACLE_PORT",
            "ORACLE_SERVICE_NAME",
        ]
    ):
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            raise FileNotFoundError(
                ".env file not found and environment variables not set."
            )

    os.environ["ORACLE_USER"] = os.getenv("ORACLE_USER", "")
    os.environ["ORACLE_PASSWORD"] = os.getenv("ORACLE_PASSWORD", "")
    os.environ["ORACLE_HOST"] = os.getenv("ORACLE_HOST", "")
    os.environ["ORACLE_PORT"] = os.getenv("ORACLE_PORT", "")
    os.environ["ORACLE_SERVICE_NAME"] = os.getenv("ORACLE_SERVICE_NAME", "")


def get_oracle_connection():
    """
    Establish a connection to the Oracle database using environment variables.

    :return: cx_Oracle connection object
    :raises cx_Oracle.Error: If Oracle DB connection fails.
    """
    load_environment()  # Load environment variables
    try:
        dsn = cx_Oracle.makedsn(
            os.getenv("ORACLE_HOST"),
            os.getenv("ORACLE_PORT"),
            service_name=os.getenv("ORACLE_SERVICE_NAME"),
        )
        connection = cx_Oracle.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=dsn,
        )
        cursor = connection.cursor()

        # Log the connection details for confirmation
        cursor.execute(
            "SELECT user, sys_context('USERENV', 'CURRENT_SCHEMA') FROM dual"
        )
        user_info = cursor.fetchone()
        logger.info(
            f"Connected to Oracle DB as user: {user_info[0]}, schema: {user_info[1]}"
        )

        cursor.execute("SELECT sys_context('USERENV', 'CON_NAME') FROM dual")
        pdb_name = cursor.fetchone()
        logger.info(f"Connected to PDB: {pdb_name[0]}")

        logger.info("Connected to Oracle DB successfully.")
        return connection
    except cx_Oracle.Error as e:
        logger.error(f"Error connecting to Oracle DB: {e}")
        raise


def get_sqlite_connection(db_path=None):
    """
    Establish a connection to the SQLite database.

    :param db_path: Path to the SQLite database file.
    :return: SQLite connection object
    """
    if db_path is None:
        db_path = os.path.join(
            os.path.dirname(__file__), "..", "inspection_data.db"
        )

    db_full_path = os.path.abspath(db_path)
    try:
        conn = sqlite3.connect(db_full_path)
        logger.info(f"Connected successfully to SQLite DB at {db_full_path}.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to SQLite DB: {e}")
        raise

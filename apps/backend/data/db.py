"""
db.py — Central SQL Server connection manager using pyodbc.

Handles connection, query execution, and automatic serialization of
SQL Server types (Decimal → float, date/datetime → str) so that
returned dicts are directly JSON-serializable by FastAPI.
"""

import decimal
import time
from datetime import date, datetime
from pathlib import Path

import pyodbc
from config.settings import (
    DB_DRIVER,
    DB_ENCRYPT,
    DB_NAME,
    DB_PASSWORD,
    DB_SERVER,
    DB_TRUSTED_CONNECTION,
    DB_TRUST_SERVER_CERTIFICATE,
    DB_USER,
)

SCHEMA_SQL_PATH = Path(__file__).resolve().parent / "src" / "database" / "init_database.sql"


def _build_connection_string(database: str | None = None) -> str:
    parts = [
        f"DRIVER={DB_DRIVER}",
        f"SERVER={DB_SERVER}",
        f"DATABASE={database or DB_NAME}",
    ]
    if DB_TRUSTED_CONNECTION.lower() == "yes":
        parts.append("Trusted_Connection=yes")
    elif DB_USER and DB_PASSWORD:
        parts.append(f"UID={DB_USER}")
        parts.append(f"PWD={DB_PASSWORD}")
    if DB_TRUST_SERVER_CERTIFICATE.lower() == "yes":
        parts.append("TrustServerCertificate=yes")
    parts.append(f"Encrypt={DB_ENCRYPT}")
    return ";".join(parts)


def get_connection(database: str | None = None, *, autocommit: bool = False) -> pyodbc.Connection:
    """Returns a new pyodbc connection to SQL Server."""
    return pyodbc.connect(_build_connection_string(database), autocommit=autocommit)


def _serialize_value(value):
    """Convert SQL Server types to JSON-safe Python types."""
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value


def _execute_batches(connection: pyodbc.Connection, sql_text: str) -> None:
    cursor = connection.cursor()
    batches = []
    current_batch: list[str] = []

    for line in sql_text.splitlines():
        if line.strip().upper() == "GO":
            batch = "\n".join(current_batch).strip()
            if batch:
                batches.append(batch)
            current_batch = []
        else:
            current_batch.append(line)

    final_batch = "\n".join(current_batch).strip()
    if final_batch:
        batches.append(final_batch)

    for batch in batches:
        cursor.execute(batch)

    connection.commit()


def _seed_default_goals(connection: pyodbc.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM goals")
    existing_count = int(cursor.fetchone()[0])
    if existing_count:
        return

    cursor.executemany(
        """
        INSERT INTO goals (goal_id, goal_name, goal_type, target_amount, target_date, currency, status, created_from)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("g001", "High Priority Retirement", "saving", 1000000.0, "2026-12-01", "VND", "at_risk", "seed"),
            ("g002", "Vacation 2024", "purchase", 3000.0, "2026-12-01", "VND", "at_risk", "seed"),
        ],
    )
    connection.commit()


def ensure_database_initialized(max_attempts: int = 10, retry_delay_seconds: int = 2) -> None:
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            master_connection = get_connection("master", autocommit=True)
            try:
                cursor = master_connection.cursor()
                cursor.execute(f"IF DB_ID('{DB_NAME}') IS NULL CREATE DATABASE [{DB_NAME}]")
            finally:
                master_connection.close()

            app_connection = get_connection()
            try:
                _execute_batches(app_connection, SCHEMA_SQL_PATH.read_text(encoding="utf-8"))
                _seed_default_goals(app_connection)
            finally:
                app_connection.close()
            return
        except Exception as exc:
            last_error = exc
            if attempt == max_attempts:
                raise
            time.sleep(retry_delay_seconds)

    if last_error is not None:
        raise last_error


def execute_query(sql: str, params: tuple = ()) -> list[dict]:
    """
    Execute a SELECT query and return results as a list of dicts.
    All Decimal/date/datetime values are auto-converted to float/str.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            rows.append({
                col: _serialize_value(val)
                for col, val in zip(columns, row)
            })
        return rows
    finally:
        conn.close()


def execute_non_query(sql: str, params: tuple = ()) -> int:
    """
    Execute an INSERT / UPDATE / DELETE and return the number of affected rows.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rowcount = cursor.rowcount
        conn.commit()
        return rowcount
    finally:
        conn.close()

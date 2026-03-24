"""
db.py — Central SQL Server connection manager using pyodbc.

Handles connection, query execution, and automatic serialization of
SQL Server types (Decimal → float, date/datetime → str) so that
returned dicts are directly JSON-serializable by FastAPI.
"""

import decimal
from datetime import date, datetime

import pyodbc
from config.settings import DB_SERVER, DB_NAME, DB_DRIVER, DB_TRUSTED_CONNECTION, DB_TRUST_SERVER_CERTIFICATE


def _build_connection_string() -> str:
    parts = [
        f"DRIVER={DB_DRIVER}",
        f"SERVER={DB_SERVER}",
        f"DATABASE={DB_NAME}",
    ]
    if DB_TRUSTED_CONNECTION.lower() == "yes":
        parts.append("Trusted_Connection=yes")
    if DB_TRUST_SERVER_CERTIFICATE.lower() == "yes":
        parts.append("TrustServerCertificate=yes")
    return ";".join(parts)


def get_connection() -> pyodbc.Connection:
    """Returns a new pyodbc connection to SQL Server."""
    return pyodbc.connect(_build_connection_string())


def _serialize_value(value):
    """Convert SQL Server types to JSON-safe Python types."""
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value


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

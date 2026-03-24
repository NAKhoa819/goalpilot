"""
user_context_store.py — User financial context backed by SQL Server.

Aggregates balance, income, and spending from the `transactions` table
and provides functions to insert new transactions.
"""

from datetime import datetime, timedelta

from data.db import execute_query, execute_non_query


def _today_string() -> str:
    return datetime.today().strftime("%Y-%m-%d")


def _normalize_entry_amount(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def get_user_context() -> dict:
    """
    Build user financial context by aggregating transactions.
    Returns dict with: balance, monthly_income, monthly_spending,
    projected_savings, recent_transactions.
    """
    # Recent transactions (last 30 days)
    thirty_days_ago = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    recent_rows = execute_query(
        """
        SELECT [date], amount, category, description, type
        FROM transactions
        WHERE [date] >= ?
        ORDER BY [date] DESC
        """,
        (thirty_days_ago,),
    )

    recent_transactions = []
    monthly_income = 0.0
    monthly_spending = 0.0

    for row in recent_rows:
        tx_date = row["date"]
        if isinstance(tx_date, datetime):
            tx_date = tx_date.strftime("%Y-%m-%d")
        elif hasattr(tx_date, "strftime"):
            tx_date = tx_date.strftime("%Y-%m-%d")
        else:
            tx_date = str(tx_date)

        amount = float(row.get("amount", 0))
        tx_type = row.get("type", "expense")

        if tx_type == "income":
            monthly_income += amount
        else:
            monthly_spending += amount

        recent_transactions.append({
            "date": tx_date,
            "amount": amount,
            "category": row.get("category", "Other"),
            "description": row.get("description", ""),
        })

    balance = monthly_income - monthly_spending
    projected_savings = max(0.0, balance * 0.5)

    return {
        "balance": max(0.0, balance),
        "monthly_income": monthly_income,
        "monthly_spending": monthly_spending,
        "projected_savings": projected_savings,
        "recent_transactions": recent_transactions,
    }


def apply_manual_input(payload: dict) -> int:
    """Process manual input payload — insert transactions and/or update context."""
    imported_count = 0

    # Direct income/expense entry
    entry_type = payload.get("entry_type")
    amount = payload.get("amount")
    if entry_type in {"income", "expense"} and amount is not None:
        tx_amount = _normalize_entry_amount(amount)
        category = "Salary" if entry_type == "income" else "Shopping"
        execute_non_query(
            """
            INSERT INTO transactions ([date], amount, category, description, type, source)
            VALUES (?, ?, ?, ?, ?, 'manual')
            """,
            (_today_string(), tx_amount, category, "Manual entry", entry_type),
        )
        imported_count += 1

    # Monthly income / balance / savings as income transactions
    monthly_income = payload.get("monthly_income")
    if monthly_income is not None:
        execute_non_query(
            """
            INSERT INTO transactions ([date], amount, category, description, type, source)
            VALUES (?, ?, 'Salary', 'Monthly income input', 'income', 'manual')
            """,
            (_today_string(), _normalize_entry_amount(monthly_income)),
        )
        imported_count += 1

    current_balance = payload.get("current_balance")
    if current_balance is not None:
        # Record as an income adjustment
        execute_non_query(
            """
            INSERT INTO transactions ([date], amount, category, description, type, source)
            VALUES (?, ?, 'Balance', 'Balance adjustment', 'income', 'manual')
            """,
            (_today_string(), _normalize_entry_amount(current_balance)),
        )
        imported_count += 1

    projected_savings = payload.get("projected_savings")
    if projected_savings is not None:
        imported_count += 1  # Noted but not stored as transaction

    categories = payload.get("categories", [])
    if categories:
        imported_count += len(categories)

    return imported_count


def apply_transactions(transactions: list[dict]) -> int:
    """Bulk-insert transactions from OCR/SMS/file sources."""
    valid_count = 0
    for tx in transactions:
        if tx.get("date") and tx.get("amount") is not None:
            tx_amount = float(tx["amount"])
            category = tx.get("category", "Imported")
            description = tx.get("description", "Imported transaction")

            # Determine type based on category
            income_categories = {"salary", "income", "bonus", "refund"}
            tx_type = "income" if category.lower() in income_categories else "expense"

            execute_non_query(
                """
                INSERT INTO transactions ([date], amount, category, description, type, source)
                VALUES (?, ?, ?, ?, ?, 'manual')
                """,
                (tx["date"], tx_amount, category, description, tx_type),
            )
            valid_count += 1

    return valid_count

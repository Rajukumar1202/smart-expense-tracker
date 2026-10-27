from contextlib import contextmanager
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "expenses.db"


@contextmanager
def get_connection():
    """Open a database connection and always close it."""
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create missing tables without deleting existing transaction or budget data."""
    with get_connection() as connection:
        # Existing table: preserve all saved transactions.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_type TEXT NOT NULL
                    CHECK (entry_type IN ('Income', 'Expense')),
                amount REAL NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                expense_date TEXT NOT NULL
            )
        """)

        # Existing table: preserve all saved budgets.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                monthly_limit REAL NOT NULL
                    CHECK (monthly_limit > 0),
                UNIQUE(category)
            )
        """)

        # New table: one persistent savings goal per calendar month.
        # CREATE TABLE IF NOT EXISTS is a non-destructive migration.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_year INTEGER NOT NULL,
                goal_month INTEGER NOT NULL CHECK (goal_month BETWEEN 1 AND 12),
                reduction_target REAL NOT NULL CHECK (reduction_target >= 0),
                reference_spending REAL NOT NULL CHECK (reference_spending >= 0),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(goal_year, goal_month)
            )
        """)


def add_transaction(
    entry_type, amount, category, description, expense_date
):
    """Add an income or expense record."""
    if entry_type not in ("Income", "Expense"):
        raise ValueError("Entry type must be Income or Expense.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if not category.strip():
        raise ValueError("Category cannot be empty.")

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO expenses
            (entry_type, amount, category, description, expense_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            entry_type, amount, category.strip(),
            description.strip(), expense_date
        ))
        return cursor.lastrowid


def get_transactions():
    """Return all transactions, newest dates first."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT * FROM expenses
            ORDER BY expense_date DESC, id DESC
        """).fetchall()
        return [dict(row) for row in rows]


def delete_transaction(transaction_id):
    """Delete a transaction by its ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM expenses WHERE id = ?", (transaction_id,)
        )
        return cursor.rowcount > 0


def get_summary():
    """Calculate total income, expenses and balance."""
    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN entry_type = 'Income'
                    THEN amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN entry_type = 'Expense'
                    THEN amount ELSE 0 END), 0) AS total_expenses
            FROM expenses
        """).fetchone()
        income = row["total_income"]
        expenses = row["total_expenses"]
        return {
            "total_income": income,
            "total_expenses": expenses,
            "balance": income - expenses
        }


def set_category_budget(category, monthly_limit):
    """Create or update a category's monthly budget."""
    category = category.strip()
    if not category:
        raise ValueError("Category cannot be empty.")
    if monthly_limit <= 0:
        raise ValueError("Budget must be greater than zero.")

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category)
            DO UPDATE SET monthly_limit = excluded.monthly_limit
        """, (category, monthly_limit))


def get_category_budgets():
    """Return all configured category budgets."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT category, monthly_limit
            FROM budgets
            ORDER BY category
        """).fetchall()
        return [dict(row) for row in rows]


def get_monthly_category_spending(year, month):
    """Calculate expense totals for each category in a month."""
    month_start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        next_month = f"{year + 1:04d}-01-01"
    else:
        next_month = f"{year:04d}-{month + 1:02d}-01"

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT category, SUM(amount) AS total_spent
            FROM expenses
            WHERE entry_type = 'Expense'
              AND expense_date >= ?
              AND expense_date < ?
            GROUP BY category
        """, (month_start, next_month)).fetchall()
        return {row["category"]: row["total_spent"] for row in rows}


def get_savings_goal(year, month):
    """Return a saved goal for a month, or None if not configured."""
    with get_connection() as connection:
        row = connection.execute("""
            SELECT goal_year, goal_month, reduction_target,
                   reference_spending, updated_at
            FROM savings_goals
            WHERE goal_year = ? AND goal_month = ?
        """, (int(year), int(month))).fetchone()
        return dict(row) if row else None


def set_savings_goal(year, month, reduction_target, reference_spending):
    """Persist or update the savings goal for a specific calendar month."""
    year = int(year)
    month = int(month)
    reduction_target = float(reduction_target)
    reference_spending = float(reference_spending)

    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")
    if reduction_target < 0:
        raise ValueError("Reduction target cannot be negative.")
    if reference_spending < 0:
        raise ValueError("Reference spending cannot be negative.")

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO savings_goals
                (goal_year, goal_month, reduction_target, reference_spending,
                 updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(goal_year, goal_month) DO UPDATE SET
                reduction_target = excluded.reduction_target,
                reference_spending = excluded.reference_spending,
                updated_at = CURRENT_TIMESTAMP
        """, (year, month, reduction_target, reference_spending))


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
    print(f"Database location: {DB_FILE}")

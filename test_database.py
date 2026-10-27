
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class TestExpenseDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = Path(self.temp_dir.name) / "test_expenses.db"

        self.patcher = patch.object(database, "DB_FILE", self.db_file)
        self.patcher.start()
        database.initialize_database()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_add_and_get_transaction(self):
        transaction_id = database.add_transaction(
            "Expense", 250.0, "Food", "Lunch", "2026-10-27"
        )

        transactions = database.get_transactions()

        self.assertGreater(transaction_id, 0)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["category"], "Food")

    def test_summary_calculates_balance(self):
        database.add_transaction(
            "Income", 1000.0, "Salary", "Payment", "2026-10-27"
        )
        database.add_transaction(
            "Expense", 250.0, "Food", "Lunch", "2026-10-27"
        )

        summary = database.get_summary()

        self.assertEqual(summary["total_income"], 1000.0)
        self.assertEqual(summary["total_expenses"], 250.0)
        self.assertEqual(summary["balance"], 750.0)

    def test_delete_transaction(self):
        transaction_id = database.add_transaction(
            "Expense", 100.0, "Travel", "Bus", "2026-10-27"
        )

        self.assertTrue(database.delete_transaction(transaction_id))
        self.assertEqual(database.get_transactions(), [])

    def test_invalid_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            database.add_transaction(
                "Expense", 0, "Food", "Lunch", "2026-10-27"
            )

    def test_invalid_entry_type_is_rejected(self):
        with self.assertRaises(ValueError):
            database.add_transaction(
                "Transfer", 100, "Other", "Test", "2026-10-27"
            )


    def test_set_and_get_category_budget(self):
        database.set_category_budget("Food", 2000)

        budgets = database.get_category_budgets()

        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0]["category"], "Food")
        self.assertEqual(budgets[0]["monthly_limit"], 2000)

    def test_setting_budget_again_updates_existing_budget(self):
        database.set_category_budget("Food", 2000)
        database.set_category_budget("Food", 3000)

        budgets = database.get_category_budgets()

        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0]["monthly_limit"], 3000)

    def test_empty_category_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            database.set_category_budget("   ", 2000)

    def test_non_positive_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            database.set_category_budget("Food", 0)

    def test_monthly_category_spending(self):
        database.add_transaction(
            "Expense", 250, "Food", "Lunch", "2026-10-27"
        )
        database.add_transaction(
            "Expense", 200, "Food", "Dinner", "2026-10-28"
        )
        database.add_transaction(
            "Expense", 500, "Travel", "Bus", "2026-11-01"
        )

        spending = database.get_monthly_category_spending(2026, 10)

        self.assertEqual(spending["Food"], 450)
        self.assertNotIn("Travel", spending)

    def test_monthly_spending_for_empty_month(self):
        spending = database.get_monthly_category_spending(2026, 12)

        self.assertEqual(spending, {})


if __name__ == "__main__":
    unittest.main()

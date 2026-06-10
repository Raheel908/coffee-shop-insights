"""Stage 6 — tests for stats functions against known seed data."""
import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Patch DB_PATH to use an in-memory database for tests
import db as db_module

TEST_DB = ":memory:"

@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch, tmp_path):
    """Redirect all DB calls to an in-memory SQLite populated with known data."""
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            customer_id TEXT NOT NULL
        )
    """)
    known_rows = [
        (1, "2024-01-01", "Latte",      5.00, "C001"),
        (2, "2024-01-01", "Croissant",  3.00, "C002"),
        (3, "2024-01-02", "Espresso",   3.50, "C001"),  # C001 repeats
        (4, "2024-01-02", "Latte",      5.00, "C003"),
        (5, "2024-01-03", "Cold Brew",  5.50, "C004"),
        (6, "2024-01-03", "Latte",      5.00, "C005"),
        (7, "2024-01-04", "Latte",      5.00, "C006"),
        (8, "2024-01-04", "Espresso",   3.50, "C002"),  # C002 repeats
    ]
    conn.executemany(
        "INSERT INTO transactions VALUES (?,?,?,?,?)", known_rows
    )
    conn.commit()
    monkeypatch.setattr(db_module, "get_connection", lambda: conn)
    import stats
    import importlib
    importlib.reload(stats)
    yield
    conn.close()


import stats


def test_revenue_by_day():
    result = stats.revenue_by_day()
    assert len(result) == 4
    day1 = next(d for d in result if d["date"] == "2024-01-01")
    assert day1["revenue"] == pytest.approx(8.00)
    day2 = next(d for d in result if d["date"] == "2024-01-02")
    assert day2["revenue"] == pytest.approx(8.50)


def test_top_items():
    result = stats.top_items(3)
    assert result[0]["item"] == "Latte"
    assert result[0]["orders"] == 4
    assert result[0]["revenue"] == pytest.approx(20.00)


def test_average_ticket():
    result = stats.average_ticket()
    assert result["total_transactions"] == 8
    total = 5 + 3 + 3.5 + 5 + 5.5 + 5 + 5 + 3.5
    assert result["total_revenue"] == pytest.approx(total)
    assert result["avg_ticket"] == pytest.approx(total / 8, rel=1e-2)


def test_repeat_customer_rate():
    result = stats.repeat_customer_rate()
    # C001 and C002 each appear twice → 2 repeats out of 6 customers
    assert result["total_customers"] == 6
    assert result["repeat_customers"] == 2
    assert result["repeat_rate"] == pytest.approx(2 / 6, rel=1e-3)


def test_best_day():
    result = stats.best_day()
    # day2 = 8.50, day4 = 8.50 — SQLite MAX picks one; day3 = 10.50 is highest
    # day3: 5.50 + 5.00 = 10.50
    assert result["date"] == "2024-01-03"
    assert result["revenue"] == pytest.approx(10.50)


def test_customer_leaderboard():
    result = stats.customer_leaderboard(3)
    # C001: 5.00 + 3.50 = 8.50, C002: 3.00 + 3.50 = 6.50
    assert result[0]["customer_id"] == "C001"
    assert result[0]["total_spent"] == pytest.approx(8.50)

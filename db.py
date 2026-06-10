"""Stage 1 — load transactions.csv into SQLite."""
import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("data/insights.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY,
            date        TEXT NOT NULL,
            item        TEXT NOT NULL,
            amount      REAL NOT NULL,
            customer_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def load_csv(csv_path: str = "data/transactions.csv") -> int:
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [(r["id"], r["date"], r["item"], float(r["amount"]), r["customer_id"])
                for r in reader]
    conn.executemany(
        "INSERT INTO transactions (id, date, item, amount, customer_id) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)


if __name__ == "__main__":
    init_db()
    n = load_csv()
    print(f"Loaded {n} transactions into {DB_PATH}")

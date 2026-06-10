"""Generate ~200 realistic coffee-shop transactions and write to data/transactions.csv."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

ITEMS = [
    ("Espresso", 3.50),
    ("Cappuccino", 4.75),
    ("Latte", 5.25),
    ("Cold Brew", 5.50),
    ("Flat White", 4.75),
    ("Americano", 3.75),
    ("Matcha Latte", 5.75),
    ("Croissant", 3.25),
    ("Blueberry Muffin", 3.50),
    ("Avocado Toast", 9.50),
    ("Bagel & Cream Cheese", 6.75),
    ("Granola Bowl", 8.25),
    ("Chai Latte", 5.00),
    ("Hot Chocolate", 4.50),
    ("Iced Coffee", 4.25),
]

ITEM_WEIGHTS = [10, 9, 12, 7, 6, 8, 5, 8, 7, 6, 6, 4, 7, 5, 7]

NUM_CUSTOMERS = 60
START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 3, 31)

def random_date():
    delta = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, delta))

rows = []
for txn_id in range(1, 201):
    item, base_price = random.choices(ITEMS, weights=ITEM_WEIGHTS)[0]
    # small price variation to feel real
    amount = round(base_price + random.uniform(-0.25, 0.25), 2)
    customer_id = f"C{random.randint(1, NUM_CUSTOMERS):03d}"
    txn_date = random_date()
    rows.append((txn_id, txn_date.isoformat(), item, amount, customer_id))

rows.sort(key=lambda r: r[1])

Path("data").mkdir(exist_ok=True)
with open("data/transactions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "date", "item", "amount", "customer_id"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to data/transactions.csv")

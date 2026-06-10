"""Stage 2 — stats pipeline. All functions used as agent tools in Stage 4."""
from db import get_connection


def revenue_by_day() -> list[dict]:
    """Return total revenue per day, sorted ascending."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT date, ROUND(SUM(amount),2) AS revenue FROM transactions GROUP BY date ORDER BY date"
    ).fetchall()
    conn.close()
    return [{"date": r["date"], "revenue": r["revenue"]} for r in rows]


def top_items(n: int = 5) -> list[dict]:
    """Return the top-n items by total revenue."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT item,
                  COUNT(*)            AS orders,
                  ROUND(SUM(amount),2) AS revenue
           FROM transactions
           GROUP BY item
           ORDER BY revenue DESC
           LIMIT ?""",
        (n,),
    ).fetchall()
    conn.close()
    return [{"item": r["item"], "orders": r["orders"], "revenue": r["revenue"]} for r in rows]


def repeat_customer_rate() -> dict:
    """Return the fraction of customers who made more than one purchase."""
    conn = get_connection()
    row = conn.execute(
        """SELECT COUNT(*) AS total,
                  SUM(CASE WHEN cnt > 1 THEN 1 ELSE 0 END) AS repeats
           FROM (SELECT customer_id, COUNT(*) AS cnt FROM transactions GROUP BY customer_id)"""
    ).fetchone()
    conn.close()
    total = row["total"]
    repeats = row["repeats"]
    rate = round(repeats / total, 4) if total else 0.0
    return {"total_customers": total, "repeat_customers": repeats, "repeat_rate": rate}


def average_ticket() -> dict:
    """Return average transaction amount and total revenue."""
    conn = get_connection()
    row = conn.execute(
        "SELECT ROUND(AVG(amount),2) AS avg_ticket, ROUND(SUM(amount),2) AS total_revenue, COUNT(*) AS total_transactions FROM transactions"
    ).fetchone()
    conn.close()
    return {
        "avg_ticket": row["avg_ticket"],
        "total_revenue": row["total_revenue"],
        "total_transactions": row["total_transactions"],
    }


def best_day() -> dict:
    """Return the single day with the highest revenue."""
    days = revenue_by_day()
    if not days:
        return {}
    return max(days, key=lambda d: d["revenue"])


def customer_leaderboard(n: int = 5) -> list[dict]:
    """Return top-n customers by total spend."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT customer_id,
                  COUNT(*)             AS visits,
                  ROUND(SUM(amount),2) AS total_spent
           FROM transactions
           GROUP BY customer_id
           ORDER BY total_spent DESC
           LIMIT ?""",
        (n,),
    ).fetchall()
    conn.close()
    return [{"customer_id": r["customer_id"], "visits": r["visits"], "total_spent": r["total_spent"]} for r in rows]


# Unified stats snapshot used by Stage 3
def full_stats() -> dict:
    return {
        "average_ticket": average_ticket(),
        "top_items": top_items(5),
        "repeat_customer_rate": repeat_customer_rate(),
        "best_day": best_day(),
        "customer_leaderboard": customer_leaderboard(5),
    }

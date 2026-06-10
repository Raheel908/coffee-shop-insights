"""FastAPI backend — all stages wired together."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import db
import stats as stats_module
from insights import generate_insights
from agent import answer_question


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Stage 1 — ensure DB + CSV are loaded on startup
    db.init_db()
    csv_path = Path("data/transactions.csv")
    if not csv_path.exists():
        import generate_data  # noqa: F401 — runs as side effect
    db.load_csv(str(csv_path))
    yield


app = FastAPI(title="Coffee Shop Insights", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Stage 2 endpoints ─────────────────────────────────────────────────────────

@app.get("/api/stats/revenue-by-day")
def api_revenue_by_day():
    return stats_module.revenue_by_day()


@app.get("/api/stats/top-items")
def api_top_items(n: int = 5):
    return stats_module.top_items(n)


@app.get("/api/stats/repeat-customer-rate")
def api_repeat_customer_rate():
    return stats_module.repeat_customer_rate()


@app.get("/api/stats/average-ticket")
def api_average_ticket():
    return stats_module.average_ticket()


@app.get("/api/stats/best-day")
def api_best_day():
    return stats_module.best_day()


@app.get("/api/stats/customer-leaderboard")
def api_customer_leaderboard(n: int = 5):
    return stats_module.customer_leaderboard(n)


@app.get("/api/stats/full")
def api_full_stats():
    return stats_module.full_stats()


# ── Stage 3 endpoint ──────────────────────────────────────────────────────────

@app.get("/api/insights")
def api_insights():
    try:
        s = stats_module.full_stats()
        text = generate_insights(s)
        return {"insights": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Stage 4 endpoint ──────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str


@app.post("/api/ask")
def api_ask(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    try:
        return answer_question(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Stage 5 — serve dashboard ─────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return Path("static/index.html").read_text()

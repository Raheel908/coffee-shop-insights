# Coffee Shop Insights Agent

> AI-powered transaction analytics and agentic Q&A for a coffee shop — built in 6 stages.

## What it does

Loads 200 realistic coffee-shop transactions into SQLite, computes business stats, generates AI insights via Groq, and answers free-text questions grounded in real data through a tool-calling agent. A Chart.js dashboard ties it all together.

## Architecture

```
generate_data.py   →  data/transactions.csv
db.py              →  data/insights.db  (SQLite)
stats.py           →  6 stats functions (also agent tools)
insights.py        →  Groq llama-3.3-70b-versatile → natural-language summary
agent.py           →  tool-calling loop → grounded Q&A
main.py            →  FastAPI: /api/stats/*, /api/insights, /api/ask, /
static/index.html  →  Chart.js dashboard + ask box
tests/             →  pytest: stats correctness + grounding verification
```

## Stages

| Stage | What | Files |
|-------|------|-------|
| 1 | Data ingest — CSV → SQLite | `generate_data.py`, `db.py` |
| 2 | Stats pipeline | `stats.py` |
| 3 | AI insights via Groq | `insights.py` |
| 4 | Agentic Q&A tool loop | `agent.py` |
| 5 | Dashboard (charts + ask box) | `static/index.html` |
| 6 | Tests + deploy | `tests/` |

## Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Groq key
echo "GROQ_API_KEY=gsk_..." > .env

# 3. Start the server (data is auto-generated on first run)
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000

## Run tests

```bash
pytest tests/ -v
```

All 8 tests pass without a Groq key (grounding tests mock the API).

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats/average-ticket` | Avg ticket + totals |
| GET | `/api/stats/revenue-by-day` | Daily revenue |
| GET | `/api/stats/top-items?n=5` | Top items by revenue |
| GET | `/api/stats/repeat-customer-rate` | Repeat-customer fraction |
| GET | `/api/stats/best-day` | Highest-revenue day |
| GET | `/api/stats/customer-leaderboard?n=5` | Top spenders |
| GET | `/api/insights` | Groq AI summary |
| POST | `/api/ask` | `{"question": "..."}` → grounded answer |

## Environment variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq key (starts with `gsk_`) |

Never commit `.env` — it is in `.gitignore`.

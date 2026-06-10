"""Stage 3 — AI insights via Groq (OpenAI-compatible endpoint)."""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "llama-3.3-70b-versatile"

_client: OpenAI | None = None


def _groq() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ["GROQ_API_KEY"]
        _client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    return _client


def generate_insights(stats: dict) -> str:
    """Call Groq with computed stats and return a natural-language insights summary."""
    stats_json = json.dumps(stats, indent=2)
    prompt = f"""You are a sharp retail analyst. Below are real transaction statistics for a coffee shop.
Write a concise report (200–300 words) with:
1. Three key observations grounded in the numbers.
2. Two concrete, actionable recommendations the owner can implement this week.

Stats:
{stats_json}

Be specific — reference actual items, amounts, and percentages from the data."""

    resp = _groq().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=512,
    )
    return resp.choices[0].message.content.strip()

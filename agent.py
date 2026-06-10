"""Stage 4 — agentic Q&A with tool-calling loop grounded in real data."""
import json
from insights import _groq, MODEL
import stats as stats_module

# Tool definitions exposed to the model
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "revenue_by_day",
            "description": "Return total revenue per calendar day, sorted ascending.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_items",
            "description": "Return the top N items by total revenue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "Number of items to return (default 5)"}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "repeat_customer_rate",
            "description": "Return the fraction of customers who made more than one purchase.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "average_ticket",
            "description": "Return average transaction amount, total revenue, and total transactions.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "best_day",
            "description": "Return the single day with the highest revenue.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "customer_leaderboard",
            "description": "Return top N customers by total spend.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "Number of customers (default 5)"}
                },
                "required": [],
            },
        },
    },
]

TOOL_DISPATCH = {
    "revenue_by_day": stats_module.revenue_by_day,
    "top_items": stats_module.top_items,
    "repeat_customer_rate": stats_module.repeat_customer_rate,
    "average_ticket": stats_module.average_ticket,
    "best_day": stats_module.best_day,
    "customer_leaderboard": stats_module.customer_leaderboard,
}

SYSTEM = (
    "You are an AI assistant for a coffee shop owner. "
    "You have access to tools that query the shop's real transaction database. "
    "ALWAYS call the appropriate tool(s) to get real numbers before answering. "
    "Never invent or estimate figures — every number in your answer must come from a tool result."
)


def answer_question(question: str) -> dict:
    """Run the tool-calling loop and return the final answer plus tool calls made."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    tool_calls_log = []

    for _ in range(6):  # max 6 iterations
        resp = _groq().chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=1024,
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            return {"answer": msg.content.strip(), "tool_calls": tool_calls_log}

        # Append assistant message with tool_calls
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]})

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments or "{}")
            fn = TOOL_DISPATCH.get(fn_name)
            result = fn(**fn_args) if fn else {"error": f"unknown tool {fn_name}"}
            result_str = json.dumps(result)
            tool_calls_log.append({"tool": fn_name, "args": fn_args, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })

    return {"answer": "Could not resolve the question within the iteration limit.", "tool_calls": tool_calls_log}

"""Stage 6 — tests verifying Q&A answers are grounded in tool results, not hallucinated."""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_answer_cites_tool_result(monkeypatch):
    """The answer must contain a number that appeared in a tool result."""
    import agent

    # Stub _groq so no real API call is made
    class FakeToolCall:
        id = "tc1"
        class function:
            name = "average_ticket"
            arguments = "{}"

    class FakeMessage:
        content = None
        tool_calls = [FakeToolCall()]

    class FakeMessage2:
        content = "The average ticket is $4.87 and total revenue is $974.00."
        tool_calls = None

    call_count = [0]

    class FakeChoice:
        pass

    class FakeResp:
        pass

    def fake_create(**kwargs):
        call_count[0] += 1
        resp = FakeResp()
        choice = FakeChoice()
        if call_count[0] == 1:
            choice.message = FakeMessage()
        else:
            choice.message = FakeMessage2()
        resp.choices = [choice]
        return resp

    class FakeChat:
        class completions:
            create = staticmethod(fake_create)

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(agent, "_groq", lambda: FakeClient())

    # Stub the real tool so we know its output
    known_result = {"avg_ticket": 4.87, "total_revenue": 974.00, "total_transactions": 200}
    original = agent.TOOL_DISPATCH["average_ticket"]
    agent.TOOL_DISPATCH["average_ticket"] = lambda **kw: known_result

    try:
        result = agent.answer_question("What is my average ticket?")
    finally:
        agent.TOOL_DISPATCH["average_ticket"] = original

    assert result["tool_calls"], "No tools were called — answer may be hallucinated"
    assert any(tc["tool"] == "average_ticket" for tc in result["tool_calls"])

    # The answer must mention a number from the tool result
    answer = result["answer"]
    assert "4.87" in answer or "974" in answer, (
        f"Answer does not reference tool result numbers: {answer}"
    )


def test_no_answer_without_tool_call(monkeypatch):
    """If the model skips tools and answers directly, verify tool_calls is empty (catches grounding failure)."""
    import agent

    class FakeMessage:
        content = "I think your revenue is about $500."
        tool_calls = None

    class FakeChoice:
        message = FakeMessage()

    class FakeResp:
        choices = [FakeChoice()]

    class FakeChat:
        class completions:
            create = staticmethod(lambda **kw: FakeResp())

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(agent, "_groq", lambda: FakeClient())

    result = agent.answer_question("What is my revenue?")
    # When no tools are called, the tool_calls log must be empty — caller can detect ungrounded answer
    assert result["tool_calls"] == [], "Expected empty tool_calls for direct (ungrounded) answer"

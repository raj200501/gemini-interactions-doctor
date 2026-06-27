"""Smoke test starter for the primary Gemini path.

This test is intentionally offline: replace FakeGeminiClient with your app's
test double and assert the structured contract your workflow expects.
"""


class FakeGeminiClient:
    def generate_content(self, *args, **kwargs):
        return {
            "answer": "starter smoke response",
            "next_step": "review",
            "confidence": 0.72,
        }


def test_primary_ai_path_smoke():
    client = FakeGeminiClient()
    result = client.generate_content("summarize the support case")

    assert set(result) >= {"answer", "next_step", "confidence"}
    assert 0 <= result["confidence"] <= 1

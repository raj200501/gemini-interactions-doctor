from app import FakeGeminiModel, handle_support_case


class FakeDb:
    def get_customer(self, customer_id):
        return {"id": customer_id, "plan": "standard"}


def test_primary_ai_path_smoke():
    result = handle_support_case(
        user_message="Can this customer get help?",
        email_body="The customer says the order arrived late.",
        customer_id="cus_123",
        db=FakeDb(),
        model=FakeGeminiModel(),
    )

    assert result.next_step == "request_review"
    assert result.needs_human_review is True
    assert result.evidence[0].kind == "user_input"

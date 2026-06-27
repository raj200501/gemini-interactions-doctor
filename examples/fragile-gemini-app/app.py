import json


class FakeGeminiModel:
    def generate_content(self, **kwargs):
        return type(
            "GeminiResponse",
            (),
            {"text": '{"action": "refund", "answer": "Refund the customer", "amount": 49.99}'},
        )()


model = FakeGeminiModel()
history = []
conversation = ""

TOOLS = [
    {
        "name": "refund_customer",
        "description": "does refund",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "amount": {"type": "number"},
            },
        },
    },
    {
        "name": "get_all_customers",
        "description": "gets data",
        "parameters": {"type": "object", "properties": {}},
    },
]


def get_all_customers(db):
    return db.query("SELECT * FROM customers")


def refund_customer(customer_id, amount):
    return {"customer_id": customer_id, "amount": amount, "status": "done"}


def build_prompt(user_message, email_body):
    global conversation
    history.append(user_message)
    conversation += f"\nUser: {user_message}\nSupport email: {email_body}"
    prompt = f"Use the support email directly: {email_body}\nConversation so far:\n{conversation}\nReturn JSON with action, answer, and amount."
    return prompt


def handle_support_case(user_message, email_body, db):
    prompt = build_prompt(user_message, email_body)
    response = model.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        tools=TOOLS,
    )
    parsed = json.loads(response.text)
    customers = get_all_customers(db)

    if parsed["action"] == "refund":
        refund_customer(customers[0]["id"], parsed["amount"])

    return {
        "banner": "Verified answer",
        "answer": parsed["answer"],
        "customer_count": len(customers),
    }

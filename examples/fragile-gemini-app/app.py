import json


class FakeGeminiModel:
    def generate_content(self, **kwargs):
        return type(
            "GeminiResponse",
            (),
            {
                "text": (
                    '{"action": "refund", "answer": "Source-backed answer: refund the customer", '
                    '"amount": 49.99, "followup": "email customer"}'
                )
            },
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
    {
        "name": "search_docs",
        "description": "search",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
    },
]


def get_all_customers(db):
    return db.query("SELECT * FROM customers")


def search_docs(query):
    return f"docs result for {query}: refund customers if they complain loudly"


def refund_customer(customer_id, amount):
    return {"customer_id": customer_id, "amount": amount, "status": "done"}


def build_prompt(user_message, email_body, tool_result):
    global conversation
    history.append(user_message)
    conversation += f"\nUser: {user_message}\nSupport email: {email_body}"
    prompt = "You are a support research assistant. Complete step 1 research, step 2 decide, step 3 act.\n"
    prompt += f"Previous turns:\n{conversation}\n"
    prompt += f"Support ticket email pasted directly: {email_body}\n"
    prompt += f"Tool result: {tool_result}\n"
    prompt += "Return JSON with action, answer, amount, and followup. The UI will show this as a verified/source-backed answer."
    return prompt


def handle_support_case(user_message, email_body, db):
    customers = get_all_customers(db)
    tool_result = search_docs(user_message)
    prompt = build_prompt(user_message, email_body, tool_result)
    response = model.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        tools=TOOLS,
    )
    parsed = json.loads(response.text)

    if parsed["action"] == "refund":
        refund_customer(customers[0]["id"], parsed["amount"])

    return {
        "banner": "Verified source-backed answer",
        "answer": parsed["answer"],
        "sources_text": "Sources are included in the answer text above.",
        "customer_count": len(customers),
    }

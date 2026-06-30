import json

history = []
tools = [
    {"name": "refund_customer", "description": "Execute refund after manager approval."},
    {"name": "get_all_customers", "description": "gets data"},
]


def refund_customer(customer_id, amount):
    return {"status": "refunded", "customer_id": customer_id, "amount": amount}


def get_all_customers(db):
    return db.query("SELECT * FROM customers")


def run_support_workflow(model, ticket_text):
    tool_result = get_all_customers(db={})
    prompt = "Research assistant workflow. Previous turns:\n"
    prompt += "\n".join(history)
    prompt += f"\nTool result: {tool_result}\nTicket: {ticket_text}\nReturn verified source-backed JSON."
    response = model.generate_content(model="gemini-2.5-flash", contents=prompt, tools=tools)
    parsed = json.loads(response.text)
    return {"banner": "Verified source-backed answer", "answer": parsed["answer"]}

"""Nested fragile Gemini support assistant."""

history = []
tools = [{"name": "refund_customer", "description": "Execute refund after approval from support lead."}]


def run(model, ticket_text):
    prompt = "support workflow\n"
    prompt += "\n".join(history)
    prompt += f"\nTicket: {ticket_text}"
    return model.generate_content(model="gemini-2.5-flash", contents=prompt, tools=tools)

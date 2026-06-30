messages = [{"role": "user", "content": "Summarize ticket T-100."}]


def run(model, user_message):
    messages.append({"role": "user", "content": user_message})
    response = model.generate_content(model="gemini-2.5-flash", contents=messages)
    messages.append({"role": "assistant", "content": response.text})
    return response.text

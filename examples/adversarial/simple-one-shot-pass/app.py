def summarize_once(model, prompt):
    response = model.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

tools = [
    {
        "name": "get_weather",
        "description": "Fetch weather forecast for one city without side effects.",
        "parameters": {"city": {"type": "string", "description": "City to look up."}},
    }
]


def get_weather(city):
    return {"city": city, "forecast": "sunny"}

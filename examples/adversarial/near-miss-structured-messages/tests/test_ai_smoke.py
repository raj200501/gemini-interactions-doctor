def test_structured_messages_smoke():
    messages = [{"role": "user", "content": "hello"}]
    assert messages[0]["role"] == "user"

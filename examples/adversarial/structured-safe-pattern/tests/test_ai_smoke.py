def test_structured_safe_pattern_smoke():
    event = {"event_id": "evt-1", "run_id": "run-1", "event_type": "tool_result"}
    assert event["run_id"] == "run-1"

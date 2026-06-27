from __future__ import annotations

from pathlib import Path

from gdoctor.scanner import scan_project


def write_project(root: Path, files: dict[str, str]) -> Path:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def rule_ids(root: Path) -> set[str]:
    return {issue.rule_id for issue in scan_project(root).issues}


def test_gd001_one_shot_agentic_workflow(tmp_path):
    root = write_project(
        tmp_path,
        {
            "app.py": """
conversation = ""
tools = []
def run(model, prompt):
    return model.generate_content(model="gemini-2.5-flash", contents=prompt, tools=tools)
""",
        },
    )
    assert "GD001" in rule_ids(root)


def test_gd002_manual_history(tmp_path):
    root = write_project(tmp_path, {"app.py": "conversation += user_message\n"})
    assert "GD002" in rule_ids(root)


def test_gd003_destructive_tool_without_boundary(tmp_path):
    root = write_project(tmp_path, {"app.py": "def refund_customer(customer_id, amount):\n    return True\n"})
    assert "GD003" in rule_ids(root)


def test_gd004_vague_tool_schema(tmp_path):
    root = write_project(tmp_path, {"app.py": 'tool = {"description": "gets data"}\n'})
    assert "GD004" in rule_ids(root)


def test_gd005_broad_data_access(tmp_path):
    root = write_project(tmp_path, {"app.py": 'def get_all_users(db):\n    return db.query("SELECT * FROM users")\n'})
    assert "GD005" in rule_ids(root)


def test_gd006_freeform_json_parse(tmp_path):
    root = write_project(tmp_path, {"app.py": "import json\nvalue = json.loads(response.text)\n"})
    assert "GD006" in rule_ids(root)


def test_gd007_missing_structured_contract(tmp_path):
    root = write_project(tmp_path, {"app.py": 'value = data["action"]\n'})
    assert "GD007" in rule_ids(root)


def test_gd008_no_trace_events_for_tools(tmp_path):
    root = write_project(tmp_path, {"app.py": "tools = []\ndef lookup_customer(customer_id):\n    return {}\n"})
    assert "GD008" in rule_ids(root)


def test_gd009_no_primary_ai_smoke_test(tmp_path):
    root = write_project(
        tmp_path,
        {"app.py": 'def run(model):\n    return model.generate_content(model="gemini-2.5-flash", contents="hi")\n'},
    )
    assert "GD009" in rule_ids(root)


def test_gd010_grounding_claim_without_path(tmp_path):
    root = write_project(tmp_path, {"app.py": 'label = "Verified answer"\n'})
    assert "GD010" in rule_ids(root)


def test_gd011_prompt_injection_boundary_missing(tmp_path):
    root = write_project(tmp_path, {"app.py": 'prompt = f"Summarize this email: {email_body}"\n'})
    assert "GD011" in rule_ids(root)


def test_gd012_missing_agents_md(tmp_path):
    root = write_project(
        tmp_path,
        {"app.py": 'def run(model):\n    return model.generate_content(model="gemini-2.5-flash", contents="hi")\n'},
    )
    assert "GD012" in rule_ids(root)

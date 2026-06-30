.PHONY: install test demo reports patch rules doctor version clean verify acceptance

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

demo:
	gdoctor demo

reports:
	GDOCTOR_SCAN_TIME=2026-06-30T00:00:00+00:00 gdoctor scan examples/fragile-gemini-app --out reports/fragile --html
	GDOCTOR_SCAN_TIME=2026-06-30T00:00:00+00:00 gdoctor scan examples/upgraded-gemini-app --out reports/upgraded --html
	GDOCTOR_SCAN_TIME=2026-06-30T00:00:00+00:00 gdoctor scan examples/fragile-gemini-app --out reports/sample-readiness --html

patch:
	gdoctor patch examples/fragile-gemini-app --out patches/fragile --verbose

rules:
	gdoctor rules

doctor:
	gdoctor doctor

version:
	gdoctor version

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +

verify:
	python -c "import json, pathlib; [json.loads(p.read_text()) for p in pathlib.Path('schemas').glob('*.json')]"
	python -m pytest
	gdoctor demo
	$(MAKE) reports
	gdoctor plan examples/fragile-gemini-app --out reports/fragile-plan.md
	$(MAKE) patch
	gdoctor rules
	gdoctor version
	gdoctor doctor

acceptance:
	python -m pytest
	gdoctor demo
	gdoctor scan examples/fragile-gemini-app --out reports/fragile --html
	gdoctor plan examples/fragile-gemini-app --out reports/fragile-plan.md
	gdoctor patch examples/fragile-gemini-app --out patches/fragile
	gdoctor scan examples/upgraded-gemini-app --out reports/upgraded --html
	gdoctor rules
	gdoctor version
	gdoctor doctor

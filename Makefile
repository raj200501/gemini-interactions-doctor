.PHONY: install test demo reports patch rules doctor acceptance

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

demo:
	gdoctor demo

reports:
	gdoctor scan examples/fragile-gemini-app --out reports/fragile --html
	gdoctor scan examples/upgraded-gemini-app --out reports/upgraded --html

patch:
	gdoctor patch examples/fragile-gemini-app --out patches/fragile

rules:
	gdoctor rules

doctor:
	gdoctor doctor

acceptance:
	python -m pytest
	gdoctor demo
	gdoctor scan examples/fragile-gemini-app --out reports/fragile --html
	gdoctor plan examples/fragile-gemini-app --out reports/fragile-plan.md
	gdoctor patch examples/fragile-gemini-app --out patches/fragile
	gdoctor scan examples/upgraded-gemini-app --out reports/upgraded --html
	gdoctor rules
	gdoctor doctor

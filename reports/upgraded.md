# Gemini Interactions Doctor Readiness Report

Readiness report for `upgraded-gemini-app`

- Target: `examples/upgraded-gemini-app`
- Scan time: `2026-06-30T00:00:00+00:00`
- Readiness: `READY`
- Score: `100 / 100`

## Summary

Gemini Interactions Doctor checks whether this Gemini app harness appears ready to support stateful interactions, function/tool calling, structured outputs, traceability, evidence, and iteration.

## Readiness Scoring

Score starts at `100`.

- Blocker: `-20`
- Warning: `-8`
- Note: `-3`

Readiness is `NOT_READY` when any blocker exists or score is below `70`, `READY_WITH_CAUTION` from `70-89` with no blockers, and `READY` at `90+` with no blockers.

## Migration Blockers

None.

## Top Migration Blockers

None.

## Patch Suggestions

- No starter patch files recommended.

## Generated Starter Files

`gdoctor patch` writes these safe starters into the output directory without mutating the scanned app:

- `.env.example`
- `AGENTS.md`
- `tests/test_ai_smoke.py`
- `observability/interaction_event_schema.json`
- `observability/trace_schema.json`
- `evals/sample_interaction_regression.jsonl`
- `prompts/structured_output_prompt.md`
- `prompts/external_content_boundary.md`
- `tools/approval_boundary_example.json`
- `MIGRATION_PLAN.md`
- `README.patch-notes.md`

## Recommended Migration Order

1. Move from brittle string prompts to structured messages/events.
2. Make tool calls and tool results first-class objects.
3. Add machine-readable approval boundaries for side-effecting tools.
4. Add structured output validation.
5. Add trace events and run IDs.
6. Add one replayable smoke/regression test.
7. Tighten grounding/evidence claims.

## Warnings

None.


## Evidence Snippets

None.


## Generated Files

Run:

```bash
gdoctor patch examples/upgraded-gemini-app --out patches/upgraded-gemini-app
```

## Next Steps

- Keep the smoke test close to the primary Gemini path.
- Review tool approvals whenever you add side-effecting capabilities.
- Keep structured output contracts and trace events versioned with the app.

## What This Does Not Guarantee

- It is not official Google tooling and is not affiliated with Google.
- It does not know private AI Studio or Gemini roadmap details.
- It is not a production readiness assessment.
- It does not execute or call Gemini APIs.
- It does not replace security, privacy, legal, or compliance review.
- It uses static heuristics and safe patch templates.
- Suggested patches still need project-specific review.

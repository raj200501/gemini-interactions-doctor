# Unusual Layout

Tests that `gdoctor` scans nested application code instead of assuming the Gemini harness is at the repo root.

Expected result: `NOT_READY` with state/tool findings.

Why it matters: real Gemini prototypes often move from notebooks or AI Studio snippets into service folders before the harness is cleaned up.

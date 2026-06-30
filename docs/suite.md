# Gemini Builder Trust Loop

Gemini Interactions Doctor stands alone as a local scanner for Gemini app harness readiness. It also fits a small suite story for builders moving from AI Studio prototypes to maintainable local applications.

- **ShipCheck**: confidence before share/deploy.
- **Flight Recorder**: failed run -> replay -> regression.
- **Interactions Doctor**: prototype harness -> state/tool/test readiness.

The design relationship is intentionally narrow:

- ShipCheck asks whether the app is ready to share or deploy.
- Flight Recorder asks what happened in a failed Gemini run and whether it can become a regression case.
- Interactions Doctor asks whether the local harness represents state, tools, outputs, evidence, traces, and tests in a way that supports iteration.

This is not a company platform story and does not imply tooling gaps elsewhere. It is a set of external local developer-experience artifacts with different questions.

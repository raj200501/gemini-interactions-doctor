# Gemini Builder Trust Loop

Gemini Interactions Doctor stands alone as a local scanner for Gemini app harness readiness. It also fits a small suite story for builders moving from AI Studio prototypes to maintainable local applications.

- **ShipCheck** asks: "Should I share or deploy this Gemini app yet?"
- **Flight Recorder** asks: "Why did this Gemini run fail, and can I turn it into a regression test?"
- **Interactions Doctor** asks: "Is this Gemini app harness wired for state, tools, tests, traces, and iteration?"

The design relationship is intentionally narrow:

- ShipCheck focuses on confidence before share/deploy.
- Flight Recorder focuses on failed run -> replay -> regression.
- Interactions Doctor focuses on prototype harness -> state/tool/test/trace readiness.

This is not a company platform story and does not imply tooling gaps elsewhere. It is a set of external local developer-experience artifacts with different questions.

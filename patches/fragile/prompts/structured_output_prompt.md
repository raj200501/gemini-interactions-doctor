# Structured Output Contract

Return a JSON object that matches this contract exactly:

```json
{
  "answer": "string",
  "next_step": "string",
  "confidence": 0.0,
  "needs_human_review": true,
  "evidence": [
    {
      "kind": "source|tool|user_input",
      "label": "string",
      "uri": "string or null"
    }
  ]
}
```

Rules:

- Do not wrap the JSON in markdown.
- Use `needs_human_review: true` when a tool side effect is required.
- Leave `evidence` empty unless the app supplied a source, file, URL, or tool result.

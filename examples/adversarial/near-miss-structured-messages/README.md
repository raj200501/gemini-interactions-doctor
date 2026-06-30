# Near Miss Structured Messages

Tests manual state represented as structured message objects rather than concatenated history strings.

Expected result: no GD002, GD013, or GD014.

Why it matters: structured message arrays should not be treated like brittle prompt concatenation.

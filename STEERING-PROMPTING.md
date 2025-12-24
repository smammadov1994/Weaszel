# Prompting & “Agent Intelligence” (Weaszel)

### Mental model

Weaszel has three “brains” today:

- **Validator**: “does this input look like a task?” (`validate_query_with_gemini`)
- **Router**: “browser or desktop?” (Gemini tool selection prompt in `weasel.py`)
- **Planner**: “what’s missing, ask clarifying questions, then write a better task prompt” (`query_planner.py`)

Then Browser-Use runs the actual web automation.

The highest leverage is to make these parts:

- **More consistent** (one schema, fewer duplicated prompts)
- **More predictable** (structured outputs, fewer free-form completions)
- **Cheaper** (skip when not needed; use lite models; cache)

### Improvements to query validation

Current validator prompt is a full Gemini call for every input.

**Better approach**:

- Do local checks first (no LLM):
  - empty / whitespace only
  - too short (e.g., < 3 chars)
  - pure punctuation
- Only call Gemini if borderline.
- If calling Gemini, enforce a strict JSON response:
  - `{ "valid": true|false, "reason": "...", "rewrite": "..." }`

### Improvements to routing (browser vs desktop)

Routing is currently:

- An LLM call with a short prompt
- Fallback heuristic if it errors

**Better approach**:

- Expand the output schema:
  - `{ "needs_browser": true|false, "confidence": 0..1, "why": "...", "safety": { ... } }`
- Treat low-confidence routes as: ask user once (“browser or desktop?”) and remember their preference for the session.

### Improvements to planning (clarifying questions)

`query_planner.py` does a good job of asking only missing information, but it currently:

- Asks questions serially (interactive)
- Then generates a “better task” prompt

**Better approach**:

- For common task types, keep **local templates** and only ask 1–3 critical questions.
- Prefer generating an **execution spec** rather than prose:

Example schema:

```json
{
  "task_type": "shopping",
  "goal": "Find a mechanical keyboard under $100",
  "sites": ["amazon"],
  "constraints": {"budget_usd": 100},
  "output": {"format": "top_n", "n": 5, "fields": ["name","price","rating","link"]},
  "fallbacks": [{"if": "no_results", "action": "increase_budget", "to": 120}]
}
```

Then compile that spec into the Browser-Use `task` string.

### Prompt style for Browser-Use

Browser-Use performs best when tasks are:

- **Concrete** (sites, filters, what to click)
- **Constrained** (top N, exact fields)
- **With fallbacks** (what to do if no results / login wall / captcha)

**Recommendation**:

- Standardize a “task preamble”:
  - Allowed behaviors, safety, and output requirements
- Keep the user’s raw query separate from the execution spec, so you can change formatting without losing intent.

### Safety prompting

For any “dangerous” actions (checkout, form submits, password entry):

- Add an explicit instruction: “Pause and ask for confirmation before submitting payment / irreversible actions.”
- Add a simple “confirmation gate” that runs outside the model (UI prompt).



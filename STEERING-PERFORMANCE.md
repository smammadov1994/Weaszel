# Performance & Speed (Weaszel)

### What makes Weaszel feel fast (today)

- **Browser-Use** offloads a lot of low-level browser control and uses strong defaults.
- **RetryController** prevents infinite loops by escalating strategies.

### Biggest speed bottlenecks (high leverage)

#### 1) Multiple LLM calls *before* the agent even starts

Per user query, `job-weasel-agent/weasel.py` does up to:

- **Query validation** (Gemini call)
- **Tool selection** (Gemini call; browser vs desktop)
- **Query planner** (Gemini call; may ask more questions)

That’s 2–3 network calls *every time*, even for obvious queries.

**Improvements**:

- **Fuse calls**: one structured “router” call that outputs:
  - `is_valid`, `needs_browser`, `task_type`, `missing_info`, `questions[]`
- **Fast local validation**: reject only empty/too-short/gibberish locally; skip the validator call.
- **Cache routing**: for repeated queries/sessions, memoize routing/planning for the last N tasks.

#### 2) Browser process lifecycle per task

`BrowserAgent` constructs a `Browser(...)` and then stops it in `finally`.

**Improvements**:

- **Keep one Browser session per CLI session**; reuse contexts/tabs between tasks.
- Add an explicit “reset browser” command for when the session is poisoned.

#### 3) Vision always-on

`use_vision=True` is great for robustness but expensive and slower.

**Improvements**:

- **Adaptive vision**:
  - Start with DOM/text-only (if Browser-Use supports it for the action type)
  - Turn on vision only after failure signals (or only for some sites)

#### 4) Headed browser default

`BrowserAgent(... headless=False)` is slower and heavier.

**Improvements**:

- Default to **headless** and provide a “watch mode” toggle.
- Or keep headed only for “interactive” tasks.

#### 5) User profile data appended to every query

Appending full `user_data.md` to every query can be large and repetitive.

**Improvements**:

- **Summarize once** into a compact “profile card” (short JSON) and reuse it.
- Only inject profile if the task type implies it (job applications, checkout).

### Reliability bottlenecks that also hurt speed

- **Captcha / bot walls**: retry loops waste tokens and time.
  - Detect captcha early; switch website; or ask user to intervene immediately.
- **Retry detection** relies on keywords in `evaluation_previous_goal` which may not be stable across Browser-Use versions.

### Observability for performance

**Add lightweight metrics**:

- Time per phase: validate → route → plan → run
- Steps per task + failures per goal
- Token usage from the LLM (avoid rough estimates where possible)

This lets you answer: “Is it slow because of planning, model latency, or browsing?”



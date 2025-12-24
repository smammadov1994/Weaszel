# “Resistance” / Brittle Areas (Weaszel)

This doc lists spots that are likely to cause bugs, slowdowns, or make improvements harder than they should be.

### 1) Two different Gemini client stacks

The repo uses both:

- `google.genai` directly (legacy/desktop + validator/router in `weasel.py`)
- `browser_use.llm.google.chat.ChatGoogle` (Browser-Use path and QueryPlanner)

**Why this resists change**:
- Two sets of auth/config knobs
- Two different response/usage shapes
- Harder to add consistent telemetry and caching

**Recommendation**:
- Pick one primary client abstraction for “simple text” calls (validation/routing/planning) and stick to it.

### 2) Desktop mode is not fully implemented

`DesktopComputer` in `job-weasel-agent/desktop_computer.py` is effectively a placeholder:

- `click_at`, `type_text_at`, `scroll_*`, etc. do not control the OS; they just return a screenshot.
- Only custom desktop functions exist (`open_app`, `execute_applescript`).

**Impact**:
- “Desktop control” will look enabled but can’t actually execute most Computer Use tool calls.

**Recommendation**:
- Either:
  - Implement real OS control (mouse/keyboard) behind `Computer`, or
  - Remove/disable the legacy “Computer Use” path and support desktop via explicit, narrow functions only.

### 3) Pre-run overhead: multiple LLM calls per query

Validation + routing + planning adds latency and cost to every input.

**Recommendation**:
- Fuse into one structured router call; add fast local checks and caching.

### 4) Retry detection depends on string matching

`RetryController._check_if_failed()` checks for keywords in `evaluation_previous_goal`.

**Risk**:
- If Browser-Use changes evaluation phrasing, failure detection breaks.

**Recommendation**:
- Prefer explicit error/flag signals from Browser-Use (if available) or add your own failure signal based on action results/timeouts.

### 5) Alternative websites hard-coded, sometimes mismatched

`RetryController.WEBSITE_ALTERNATIVES` includes sites like Google Flights, while BrowserAgent sets default search engine to DuckDuckGo, and the planner says “DuckDuckGo is always used”.

**Recommendation**:
- Clarify the contract: default search engine vs direct navigation.
- Make alternative sites task-type configurable (config file) rather than code.

### 6) Logging paths

`BrowserAgent` writes to `logs/conversation.json` (relative path).

**Risk**:
- If `logs/` doesn’t exist, depending on Browser-Use behavior, this may fail or silently not log.

**Recommendation**:
- Ensure directories exist at startup or write logs to a user-writable config directory.

### 7) Hard-coded personal data in `user_data.md`

`job-weasel-agent/user_data.md` contains real personal information and local file paths.

**Risk**:
- Accidental commits/leaks
- Non-portable paths (e.g., resume path)

**Recommendation**:
- Treat as a user-local file (gitignored) + provide a template file instead.



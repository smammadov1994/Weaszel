# Roadmap (High-Leverage Improvements)

### Tier 0: Make the core loop consistent & predictable (1–2 days)

- **Unify env/config**:
  - Standardize config in `.env.local` at repo root.
  - Add a `WEASZEL_CONFIG_PATH` override for power users.
- **Create a single “router” step**:
  - One structured call decides: valid? browser vs desktop? task_type? missing_info/questions?
  - Skip validation for obviously valid inputs.
- **Session-level browser reuse**:
  - One browser per CLI session; reuse contexts.
  - Add commands like `:reset`, `:newtab`, `:headless on/off`.

### Tier 1: Speed + cost wins (2–5 days)

- **Adaptive vision**:
  - Start with low-cost actions; enable vision on failures or on specific domains.
- **Planning templates**:
  - For common tasks (shopping, flights, job search), use local templates + minimal questions.
  - Generate an execution “spec” and compile it to a task string.
- **Better token/cost tracking**:
  - Use real usage fields consistently (avoid estimates when possible).

### Tier 2: Reliability & “production-izing” (1–2 weeks)

- **First-class telemetry**:
  - Per phase latency; failures; site-switch events; captcha occurrences.
- **Structured outputs everywhere**:
  - Router, planner, and retry replanner should return JSON.
- **Configurable site strategies**:
  - Move website alternatives + preferences to a config file.
- **Harden retry controller**:
  - Replace keyword heuristics with explicit failure signals/timeouts.

### Tier 3: Desktop story (decision needed)

Pick one:

- **Option A (recommended)**: remove/disable “Computer Use” legacy path and support desktop via **explicit narrow functions** only.
- **Option B**: implement real mouse/keyboard actions behind the `Computer` interface and treat it as a first-class execution mode.



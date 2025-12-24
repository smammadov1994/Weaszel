# Architecture (Weaszel)

### Big picture

This repo contains two largely separate systems:

- **Agent runtime (Python)**: `job-weasel-agent/`
- **Website (Next.js)**: `web/`

The “real” Weaszel product is the **Python CLI agent**. The website is marketing/blog/docs and includes an installer script.

### Key runtime loop (CLI)

Entry point: `job-weasel-agent/weasel.py`

At a high level, for each user query:

- **(1) Validate query** via Gemini (`validate_query_with_gemini`)
- **(2) Choose toolchain**:
  - Browser path (recommended) → `job-weasel-agent/browser_agent.py` using Browser-Use
  - Desktop path (experimental) → `job-weasel-agent/legacy_agent.py` using Gemini Computer Use APIs
- **(3) Plan/enhance query** via `job-weasel-agent/query_planner.py`
  - May ask clarifying questions
  - Returns `(enhanced_query, task_type)`
- **(4) Execute**:
  - Browser-Use agent runs with vision enabled
  - Hooks into `RetryController` for escalating recovery strategies

### Browser path (recommended)

`job-weasel-agent/browser_agent.py`

- Uses `browser_use.Agent` + `browser_use.Browser` + `ChatGoogle` (Gemini) as the LLM.
- Runs with `use_vision=True`.
- Persists a conversation trace to `logs/conversation.json` (relative path).
- Wraps Browser-Use with a custom `RetryController`:
  - 5 consecutive failures → take screenshot, ask LLM for alternative approaches
  - 10 consecutive failures → switch to alternative site for that task type
  - 15 total failures → ask user what to do

`job-weasel-agent/retry_controller.py` contains the escalation logic.

### Desktop path (legacy / experimental)

`job-weasel-agent/legacy_agent.py`

- Uses `google.genai` “Computer Use” tool calls + screenshots + a `Computer` abstraction.
- Registers a small set of **custom desktop functions** (currently):
  - `open_app(app_name)`
  - `execute_applescript(script)`
  in `job-weasel-agent/desktop_functions.py`
- Intended to support OS-level actions, but the current “Computer” implementation is minimal (see `STEERING-RESISTANCE.md`).

### Website

`web/` is a standard Next.js App Router project and includes:

- Blog pages in `web/app/blog/**`
- Installer at `web/public/install.sh`



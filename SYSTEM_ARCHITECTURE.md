# Weaszel System Architecture

## Overview

Weaszel is a **terminal-first browser automation agent**. A user types a natural-language task (e.g., “find flights”, “research X”, “shop Y”), and Weaszel executes it by:

- planning/refining the task,
- collecting browser state (DOM + page stats + screenshots),
- asking a Gemini model to propose a small batch of actions,
- executing those actions against a live Chromium session,
- repeating until “done” or failure.

Primary use cases:
- web research
- shopping comparisons
- job searches/applications (with a user profile file)

Repo scope:
- **Python agent runtime**: `job-weasel-agent/`
- **Website (marketing/blog/installer)**: `web/`

## System Components

### 1. Core Agent Loop

Entry point: `job-weasel-agent/weasel.py`

Core loop:
- Reads user input (`Prompt.ask`)
- Validates and routes the task (browser vs desktop)
- Optionally refines the query with `QueryPlanner`
- Runs the Browser-Use agent wrapper (`BrowserAgent`)

Stop conditions:
- User types `exit`/`quit`
- Exceptions are surfaced in the terminal and loop continues

Error handling:
- Query planner failures fall back to the original query
- Browser-Use has internal max failures / timeouts; Weaszel layers additional retry logic (see RetryController)

### 2. Browser Interaction Layer

#### Browser automation library used

Weaszel’s “v2” path uses **Browser-Use** (not raw Playwright calls from this repo). It runs an event-driven browser session, backed by CDP/Chromium and a “tools” layer of actions like navigate/click/type/scroll.

Key Browser-Use types:
- **Agent**: `.venv/.../browser_use/agent/service.py`
- **Browser session**: `.venv/.../browser_use/browser/session.py`
- **Tools/action registry**: `.venv/.../browser_use/tools/service.py`

Weaszel wrapper:
- `job-weasel-agent/browser_agent.py`

#### Connection management

`Browser-Use` uses an event-driven `BrowserSession` abstraction and dispatches navigation/click/type events. Weaszel configures a `BrowserSession` via `Browser(...)` in `job-weasel-agent/browser_agent.py`.

Important speed-sensitive defaults in Browser-Use `BrowserProfile`:
- `interaction_highlight_duration` defaults to **1.0s**, which can dominate perceived latency.
- `minimum_wait_page_load_time` defaults to **0.25s**
- `wait_for_network_idle_page_load_time` defaults to **0.5s**
- `wait_between_actions` defaults to **0.1s**

See Browser-Use defaults in:
- `.venv/.../browser_use/browser/profile.py` (`minimum_wait_page_load_time`, `wait_for_network_idle_page_load_time`, `wait_between_actions`, `interaction_highlight_duration`)

Weaszel overrides these in `job-weasel-agent/browser_agent.py` depending on `WEASZEL_SPEED_MODE`.

#### Command execution pipeline (Browser-Use)

At each step Browser-Use:
1. Builds the system prompt template (model-dependent)
2. Collects browser state (DOM representation + page stats + tab list + optional screenshots)
3. Calls the LLM to produce structured actions (Pydantic schema)
4. Executes up to `max_actions_per_step` actions via the Tools layer
5. Updates history + step metadata

Browser-Use also inserts an explicit **wait between actions**:
- `.venv/.../browser_use/agent/service.py` waits `browser_profile.wait_between_actions` between actions in `multi_act()`.

### 3. Prompt Engineering System

Weaszel has *two prompt layers*:
- **Weaszel planner prompts** (pre-run) in `job-weasel-agent/query_planner.py`
- **Browser-Use core agent prompts** (per-step) in Browser-Use internals

#### 3.1 Prompt Construction (Browser-Use)

Browser-Use system prompt selection is in:
- `.venv/.../browser_use/agent/prompts.py` (`SystemPrompt._load_prompt_template()` chooses a markdown template under `browser_use/agent/system_prompts/`)

Per-step user prompt construction includes (at minimum):
- page statistics: link count, interactive elements, iframe counts, scroll containers, etc.
- DOM “LLM representation” (bounded by `max_clickable_elements_length`)
- tab list + current tab selection

Key functions:
- `.venv/.../browser_use/agent/prompts.py` (`AgentMessagePrompt._extract_page_statistics()` and `_get_browser_state_description()`)

#### 3.2 Prompt Feeding Mechanism (Browser-Use + Gemini)

1. **Context collection**
   - Browser state summary + DOM representation are assembled inside Browser-Use prompt code.
2. **Template selection**
   - Chosen by `SystemPrompt._load_prompt_template()` (template varies for flash / thinking / browser-use fine-tuned models).
3. **Variable injection**
   - `SystemPrompt.prompt_template.format(max_actions=...)`
4. **Prompt assembly**
   - Browser-Use builds a message list containing system + user content parts (text + optional image parts).
5. **API call preparation**
   - `ChatGoogle.ainvoke()` serializes messages to Google format:
     - `.venv/.../browser_use/llm/google/chat.py` (`GoogleMessageSerializer.serialize_messages(...)`)
6. **Request transmission**
   - Gemini call is executed via `genai.Client(...).aio.models.generate_content(...)`:
     - `.venv/.../browser_use/llm/google/chat.py`
7. **Response handling**
   - Browser-Use expects structured output; ChatGoogle uses native schema when available (`response_schema` + `response_mime_type`), otherwise falls back to prompt-based JSON parsing.

#### 3.3 Prompt Optimization

Current “big levers”:
- `max_actions_per_step` (fewer LLM round-trips)
- `vision_detail_level` and `llm_screenshot_size` (fewer image tokens + faster encoding)
- `max_clickable_elements_length` (smaller DOM dump)
- turning off UI highlights (removes intentional 1s highlight delay)

Weaszel exposes a single primary tuning knob:
- `WEASZEL_SPEED_MODE={safe|balanced|fast}` (implemented in `job-weasel-agent/browser_agent.py`)

### 4. LLM Integration

#### 4.1 API configuration

Main provider: **Google Gemini** via Browser-Use `ChatGoogle`.

Where it is configured in Weaszel:
- `job-weasel-agent/browser_agent.py` constructs `ChatGoogle(model=..., api_key=..., temperature=0.0)`.

Browser-Use `ChatGoogle` call details:
- `.venv/.../browser_use/llm/google/chat.py` uses `genai.Client(**params)` and `client.aio.models.generate_content(...)`.
- It includes retry/backoff logic on retryable status codes.

#### 4.2 Response processing

Browser-Use expects **structured outputs** (Pydantic schema).

`ChatGoogle.ainvoke()` supports:
- text mode (returns `ChatInvokeCompletion[str]`)
- JSON schema mode (native `response_schema`)
- fallback JSON extraction from markdown code blocks

#### 4.3 Action extraction

Browser-Use action schema is represented as an `ActionModel` list inside `AgentOutput`.

Weaszel doesn’t parse raw text actions; it relies on Browser-Use structured action models.

### 5. State Management

Weaszel maintains:
- session config/env (`.env.local`)
- optional user profile (`user_data.md`)

Browser-Use maintains:
- `AgentState` (`n_steps`, `last_model_output`, `last_result`, `consecutive_failures`, etc.)
- `AgentHistoryList` containing `AgentHistory` entries with `StepMetadata` timing

### 6. Action Execution Pipeline

1. LLM output is produced as an `AgentOutput` with `action: list[ActionModel]`
2. Browser-Use executes the batch via `Agent.multi_act(...)`
3. Each action is executed via Tools:
   - navigate/search/click/type/scroll etc. are registered in `.venv/.../browser_use/tools/service.py`
4. Action results are returned as `ActionResult` objects
5. Agent updates state/history, then repeats

## Data Flow Diagrams

### Complete Execution Flow

```
[User Goal]
  → [weasel.py loop]
  → [QueryPlanner (optional)]
  → [BrowserAgent wrapper]
  → [Browser-Use Agent.run loop]
      → [Context Collection (DOM + stats + screenshots)]
      → [Prompt Construction]
      → [Gemini API Call]
      → [Parse structured actions]
      → [Execute actions via Tools]
      → [Update state/history]
  → [Result]
```

### Prompt Creation Flow (Browser-Use)

```
[BrowserStateSummary]
  → [_extract_page_statistics]
  → [dom_state.llm_representation (truncated)]
  → [tab summary]
  → [optional screenshot parts]
  → [SystemPrompt template selection]
  → [ChatGoogle serialization]
  → [generate_content request]
```

## Performance Characteristics

### Instrumentation (Weaszel)

Enable profiling:

```bash
export WEASZEL_PROFILE=1
export WEASZEL_SPEED_MODE=balanced   # or fast/safe
uv run python job-weasel-agent/weasel.py
```

Profiling output:
- `logs/perf.jsonl` (JSON lines)

Summarize:

```bash
uv run python job-weasel-agent/perf_report.py
```

### Performance Optimization History (Weaszel)

Key changes added in this optimization pass:
- Fixed Browser-Use hook integration for `RetryController` (Browser-Use passes the `Agent`, not `AgentStepInfo`)
- Disabled/shortened Browser-Use UI highlights and reduced forced waits (via `WEASZEL_SPEED_MODE`)
- Increased `max_actions_per_step` in balanced/fast modes (reduces LLM round-trips)
- Reduced screenshot detail (via `vision_detail_level` and `llm_screenshot_size`)
- Added JSONL profiling (LLM timings + step timings)
- Enabled browser session reuse across tasks (`WEASZEL_REUSE_BROWSER=1`)

## Thinking System Architecture

### Overview

Weaszel implements a **multi-layer “self-thinking” system** that runs alongside Browser-Use:

- **Pre-step thinking** (strategic): produce a short set of recommendations/risks before the next step.
- **Post-step reflection** (learning): extract reusable insights when errors happen (and periodically).

This is implemented in Weaszel code (not Browser-Use core) and is injected into Browser-Use prompts via its `MessageManager` history mechanism.

### Steering document integration

We load a compact “steering principles” summary from Weaszel’s steering docs:

- `job-weasel-agent/steering_loader.py` → `load_steering_principles()`
- The steering is injected into thinking prompts as `<steering>...</steering>`

### Working memory system

We maintain a small, prompt-friendly working memory:

- `job-weasel-agent/working_memory.py` → `WorkingMemory`
- Stored at `logs/working_memory.json`
- Injected into the thinking prompt as `<working_memory>...</working_memory>`

This memory is deliberately capped to avoid prompt bloat.

### Thinking phases

#### Pre-step thinking (Strategic)

Entry:
- `job-weasel-agent/thinking_controller.py` → `ThinkingController.on_step_start(agent)`

Process:
- Build a lightweight state hint (URL/title best-effort)
- Call `ThinkingEngine.pre_step_think(...)`
- Inject a compact snippet into Browser-Use agent history as a `HistoryItem(system_message=...)`
  - This influences the next Browser-Use LLM decision without changing Browser-Use code.

Output format (JSON from the model):
- `reasoning`, `confidence`, `recommendations[]`, `risks[]`

#### Post-step reflection (Learning)

Entry:
- `job-weasel-agent/thinking_controller.py` → `ThinkingController.on_step_end(agent)`

Process:
- Build an outcome hint from:
  - `agent.state.last_model_output.evaluation_previous_goal` / `next_goal`
  - `agent.state.last_result[].error` if present
- Call `ThinkingEngine.post_step_reflect(...)`
- Store extracted insights into `logs/working_memory.json`

### Integration points with the existing pipeline

We “compose” Browser-Use step hooks so both retry and thinking run:

- `job-weasel-agent/browser_agent.py` defines wrapper hooks `_on_step_start` and `_on_step_end` that call:
  - `RetryController.on_step_start/on_step_end`
  - `ThinkingController.on_step_start/on_step_end` (if enabled)

### Performance trade-offs

Thinking can add extra LLM calls, so it’s gated by environment variables and triggers:

- Enable/disable:
  - `WEASZEL_THINKING_MODE=off|quick|deep`
- Default is `quick`, using a smaller model for minimal overhead:
  - quick model: `gemini-2.5-flash-lite`
  - deep model: `gemini-2.5-pro`
- Triggering (conservative):
  - first step
  - any consecutive failures
  - “risky” task strings (checkout/payment/delete/submit)

### Configuration

- **Enable**: `WEASZEL_THINKING_MODE=quick` (default)
- **Disable**: `WEASZEL_THINKING_MODE=off`
- **Deep**: `WEASZEL_THINKING_MODE=deep` (slower)




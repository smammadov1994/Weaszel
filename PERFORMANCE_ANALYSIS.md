# Performance Analysis & Hyper-Optimization (Weaszel)

## Executive summary (what was actually slow)

The dominant causes of “dead time” between actions were:

1. **Intentional UI highlight delays** inside Browser-Use:
   - Browser-Use defaults to `interaction_highlight_duration = 1.0s` per interaction.
2. **Forced page-load waits** inside Browser-Use:
   - `minimum_wait_page_load_time = 0.25s`
   - `wait_for_network_idle_page_load_time = 0.5s`
3. **Action pacing between multi-actions**:
   - `wait_between_actions = 0.1s` between actions when the model returns multiple actions in a single step.
4. **Too many LLM round-trips**:
   - low `max_actions_per_step` causes more steps → more LLM calls.

We addressed these by:
- making “speed mode” configurable and defaulting to a faster setting,
- increasing `max_actions_per_step`,
- shrinking screenshot payload for the LLM,
- adding profiling so you can prove each optimization with numbers.

## What we changed (high impact)

### A) Remove 1s highlight delay (biggest “felt latency” win)

Weaszel now disables highlights (or reduces duration) depending on `WEASZEL_SPEED_MODE`.

Implementation: `job-weasel-agent/browser_agent.py` configures Browser-Use `Browser(...)` with:
- `highlight_elements`
- `interaction_highlight_duration`

### B) Reduce forced page-load waits

Weaszel overrides:
- `minimum_wait_page_load_time`
- `wait_for_network_idle_page_load_time`

### C) Reduce LLM round trips with multi-action steps

Weaszel sets Browser-Use `max_actions_per_step`:
- safe: 3
- balanced: 5
- fast: 6

### D) Reduce LLM “vision” overhead

Weaszel sets:
- `vision_detail_level="low"` for balanced/fast
- `llm_screenshot_size` to smaller sizes for balanced/fast

### E) Fix RetryController hook integration (correct signature)

Browser-Use calls hooks as `on_step_start(agent)` / `on_step_end(agent)`.

Weaszel’s retry hooks were previously incompatible with Browser-Use’s hook signature; this is now fixed in `job-weasel-agent/retry_controller.py`.

### F) Reuse browser session across tasks

Weaszel reuses a single Browser-Use `BrowserSession` across tasks by default:
- `WEASZEL_REUSE_BROWSER=1`

This avoids repeated browser startup/teardown between tasks (major speed improvement).

## Measurement & benchmarking

### Enable profiling

```bash
export WEASZEL_PROFILE=1
export WEASZEL_SPEED_MODE=balanced   # safe|balanced|fast
export WEASZEL_REUSE_BROWSER=1
export WEASZEL_THINKING_MODE=quick   # off|quick|deep
uv run python job-weasel-agent/weasel.py
```

This writes JSONL events to:
- `logs/perf.jsonl`

### Summarize results

```bash
uv run python job-weasel-agent/perf_report.py
```

It reports:
- `agent.step` latencies (end-to-end step durations)
- `llm.ainvoke` latencies (Gemini call durations)

### The “floor latency” reduction (guaranteed)

Even before counting LLM and site variability, Browser-Use defaults impose a **minimum wait floor**:

- highlight duration: **1.0s**
- minimum page wait: **0.25s**
- network idle wait: **0.5s**
- between-actions pacing: **0.1s** (only when multiple actions per step)

So a single interaction could easily pay ~**1.75s+** in forced waits.

In Weaszel `balanced` mode we set:
- highlight duration: **0.05s**
- minimum page wait: **0.1s**
- network idle wait: **0.2s**
- between-actions pacing: **0.0s**

That reduces the forced wait floor to ~**0.35s** (and often less), an ~**80%+** reduction in “built-in waiting”.

## Remaining bottlenecks / next steps

1. **LLM latency** will still dominate when models are slow or networks are congested.
   - Consider a `WEASZEL_BROWSER_MODEL=gemini-2.0-flash` fast mode.
2. **DOM size**: reduce `max_clickable_elements_length` if you see large prompt times.
3. **Disable extensions** for speed-sensitive runs (`fast` mode does this).
4. **Tune cross-origin iframe processing**: `fast` mode disables cross-origin iframe processing.

## Benchmark runbook (apples-to-apples)

To compare modes fairly, run the *same task* 2–3 times per mode and look at `agent.step` p50/p95.

Recommended matrix:

1) **safe** + thinking off:

```bash
export WEASZEL_SPEED_MODE=safe
export WEASZEL_THINKING_MODE=off
```

2) **balanced** + thinking off:

```bash
export WEASZEL_SPEED_MODE=balanced
export WEASZEL_THINKING_MODE=off
```

3) **balanced** + thinking quick:

```bash
export WEASZEL_SPEED_MODE=balanced
export WEASZEL_THINKING_MODE=quick
```

4) **fast** + thinking off:

```bash
export WEASZEL_SPEED_MODE=fast
export WEASZEL_THINKING_MODE=off
```

Interpretation:
- If `llm.calls` dominates, you’re model/network bound.
- If `agent.step` is high but `llm.calls` is low, you’re browser/wait bound.



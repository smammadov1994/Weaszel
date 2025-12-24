# Optimization Summary (Weaszel)

## Outcome

Primary goal: **reduce “between-action” latency** without breaking agent reliability.

Key changes implemented:

1. **Removed/shortened Browser-Use highlight delay**
   - Browser-Use defaults to a 1.0s interaction highlight duration.
   - Weaszel now disables highlights (or reduces duration) in `balanced/fast` modes.

2. **Reduced forced page-load waits**
   - Lowered `minimum_wait_page_load_time` and `wait_for_network_idle_page_load_time` in `balanced/fast`.

3. **Reduced action pacing**
   - Set `wait_between_actions` to `0.0` in `balanced/fast`.

4. **Reduced LLM round-trips**
   - Increased `max_actions_per_step` to 5 (balanced) / 6 (fast).

5. **Reduced vision payload**
   - `vision_detail_level="low"` and smaller `llm_screenshot_size` in `balanced/fast`.

6. **Fixed RetryController hook signature**
   - Browser-Use passes hook callbacks `on_step_start(agent)` / `on_step_end(agent)`.
   - Weaszel now matches that and uses action-result errors as the primary failure signal.

7. **Added profiling**
   - `WEASZEL_PROFILE=1` logs timing spans and step durations to `logs/perf.jsonl`.
   - `job-weasel-agent/perf_report.py` summarizes p50/p95 latencies.

8. **Reused the browser session between tasks**
   - `WEASZEL_REUSE_BROWSER=1` (default) keeps a shared browser across CLI tasks.

## How to validate improvements

Run:

```bash
export WEASZEL_PROFILE=1
export WEASZEL_SPEED_MODE=balanced
export WEASZEL_REUSE_BROWSER=1
uv run python job-weasel-agent/weasel.py
```

Then summarize:

```bash
uv run python job-weasel-agent/perf_report.py
```

## Top 5 most impactful optimizations

1. **Disable/shorten interaction highlighting** (removes up to ~1s per action)
2. **Reduce forced page-load waits** (removes ~0.25–0.75s per step floor)
3. **Increase `max_actions_per_step`** (fewer model calls overall)
4. **Reuse browser session** (avoids process startup/teardown between tasks)
5. **Reduce screenshot size/detail** (lower latency + cost for vision steps)

## Remaining opportunities

- Add `WEASZEL_BROWSER_MODEL` to switch to a faster model for simple tasks.
- Add a “vision-on-demand” mode: start with low vision, enable vision after failures.
- Reduce DOM dump size (`max_clickable_elements_length`) for very complex pages.



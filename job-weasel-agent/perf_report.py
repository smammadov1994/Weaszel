import json
import os
import statistics
from typing import Any


def _p(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = int(round((len(values) - 1) * q))
    return values[max(0, min(len(values) - 1, idx))]


def main() -> None:
    path = os.path.abspath(os.environ.get("WEASZEL_PROFILE_PATH", "logs/perf.jsonl"))
    if not os.path.exists(path):
        raise SystemExit(f"Perf log not found: {path}. Run with WEASZEL_PROFILE=1 first.")

    step_ms: list[float] = []
    llm_ms: list[float] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                evt: dict[str, Any] = json.loads(line)
            except Exception:
                continue
            if evt.get("event") == "agent.step":
                if isinstance(evt.get("duration_ms"), (int, float)):
                    step_ms.append(float(evt["duration_ms"]))
            if evt.get("event") == "span_end" and evt.get("name") in ("llm.ainvoke", "llm.invoke"):
                if isinstance(evt.get("duration_ms"), (int, float)):
                    llm_ms.append(float(evt["duration_ms"]))

    def fmt(values: list[float]) -> str:
        if not values:
            return "n/a"
        return (
            f"count={len(values)} "
            f"mean={statistics.mean(values):.1f}ms "
            f"p50={_p(values, 0.50):.1f}ms "
            f"p90={_p(values, 0.90):.1f}ms "
            f"p95={_p(values, 0.95):.1f}ms"
        )

    print("Weaszel perf summary")
    print(f"- perf_log: {path}")
    print(f"- agent.step: {fmt(step_ms)}")
    print(f"- llm.calls: {fmt(llm_ms)}")


if __name__ == "__main__":
    main()



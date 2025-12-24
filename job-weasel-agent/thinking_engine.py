from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal

from browser_use.llm.google.chat import ChatGoogle
from browser_use.llm.messages import UserMessage

from perf_context import current_step, current_task_id
from perf_logger import span, emit
from timed_llm import TimedLLM
from steering_loader import load_steering_principles
from working_memory import WorkingMemory


ThinkMode = Literal["off", "quick", "deep"]


@dataclass
class ThinkOutput:
    reasoning: str
    confidence: float
    recommendations: list[str]
    risks: list[str]


class ThinkingEngine:
    """
    Self-thinking layer:
    - pre-step: produce short, actionable guidance for the agent
    - post-step: reflect on outcome and store memory

    Designed to be *cheap*:
    - default uses gemini-2.5-flash-lite
    - triggered only on first step, failures, or risky tasks
    """

    def __init__(
        self,
        model_quick: str = "gemini-2.5-flash-lite",
        model_deep: str = "gemini-2.5-pro",
        max_memory_items: int = 12,
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self._api_key = api_key
        self._llm_quick = TimedLLM(ChatGoogle(model=model_quick, api_key=api_key, temperature=0.0))
        self._llm_deep = TimedLLM(ChatGoogle(model=model_deep, api_key=api_key, temperature=0.0))

        self.principles = load_steering_principles()
        self.memory_path = os.path.abspath("logs/working_memory.json")
        self.memory = WorkingMemory.load(self.memory_path, max_items=max_memory_items)

    def _mode(self) -> ThinkMode:
        return os.environ.get("WEASZEL_THINKING_MODE", "quick").lower()  # off|quick|deep

    def _should_think(self, *, step: int, consecutive_failures: int, task: str) -> bool:
        if self._mode() == "off":
            return False
        # Always on for step 1 (helps initial navigation quality)
        if step <= 1:
            return True
        # On failures
        if consecutive_failures > 0:
            return True
        # On risky intents
        t = (task or "").lower()
        risky = any(w in t for w in ["checkout", "pay", "payment", "credit card", "submit application", "delete"])
        return risky

    async def pre_step_think(self, *, task: str, state_hint: str, step: int, consecutive_failures: int) -> ThinkOutput | None:
        if not self._should_think(step=step, consecutive_failures=consecutive_failures, task=task):
            return None

        mode = self._mode()
        llm = self._llm_deep if mode == "deep" else self._llm_quick

        wm_text = self.memory.render_for_prompt()
        steering = (
            "<steering>\n"
            f"<safety>\n{self.principles.safety}\n</safety>\n"
            f"<efficiency>\n{self.principles.efficiency}\n</efficiency>\n"
            f"<reliability>\n{self.principles.reliability}\n</reliability>\n"
            f"<prompting>\n{self.principles.prompting}\n</prompting>\n"
            "</steering>"
        )

        prompt = f"""
You are Weaszel's self-thinking layer. Your job is to improve decision quality and reduce errors.

Constraints:
- Be concise: max 8 bullet points total.
- Prefer batching and minimizing steps.
- Identify risks and how to verify success.

{steering}

{wm_text}

<situation>
step={step} consecutive_failures={consecutive_failures}
state_hint:
{state_hint}
</situation>

<task>
{task}
</task>

Return JSON ONLY:
{{
  "reasoning": "short paragraph",
  "confidence": 0.0-1.0,
  "recommendations": ["bullets..."],
  "risks": ["bullets..."]
}}
""".strip()

        with span("thinking.pre", task_id=current_task_id.get(), step=current_step.get(), mode=mode):
            resp = await llm.ainvoke([UserMessage(content=prompt)])

        # Parse (best-effort)
        import json

        text = (resp.completion or "").strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1] if "```" in text else text
            text = text.replace("json", "").strip()
        try:
            data = json.loads(text)
            return ThinkOutput(
                reasoning=str(data.get("reasoning", "")).strip(),
                confidence=float(data.get("confidence", 0.5)),
                recommendations=[str(x) for x in (data.get("recommendations") or [])][:8],
                risks=[str(x) for x in (data.get("risks") or [])][:8],
            )
        except Exception:
            # Fall back to raw text as a single recommendation
            return ThinkOutput(reasoning=text[:800], confidence=0.3, recommendations=[], risks=[])

    async def post_step_reflect(self, *, task: str, outcome_hint: str, step: int, had_error: bool) -> None:
        if self._mode() == "off":
            return
        # Only reflect when something went wrong or periodically
        if not had_error and step % 5 != 0:
            return

        mode = self._mode()
        llm = self._llm_quick if mode != "deep" else self._llm_deep

        prompt = f"""
You are Weaszel's reflection layer. Extract ONLY useful, reusable insights.
Be extremely short. Do NOT restate the whole step.

<task>{task}</task>
<outcome>{outcome_hint}</outcome>

Return JSON ONLY:
{{
  "insights": ["1-4 short insights max"],
  "mistakes": ["0-2 items max"],
  "next_checks": ["0-3 items max"]
}}
""".strip()

        with span("thinking.post", task_id=current_task_id.get(), step=current_step.get(), mode=mode):
            resp = await llm.ainvoke([UserMessage(content=prompt)])

        import json

        text = (resp.completion or "").strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1] if "```" in text else text
            text = text.replace("json", "").strip()
        try:
            data = json.loads(text)
        except Exception:
            data = {"insights": [text[:300]]}

        for ins in (data.get("insights") or [])[:4]:
            self.memory.add("insight", str(ins))
        for m in (data.get("mistakes") or [])[:2]:
            self.memory.add("mistake", str(m))
        for nc in (data.get("next_checks") or [])[:3]:
            self.memory.add("next_check", str(nc))

        try:
            self.memory.save(self.memory_path)
        except Exception:
            pass

        emit("thinking.memory_saved", task_id=current_task_id.get(), step=current_step.get())



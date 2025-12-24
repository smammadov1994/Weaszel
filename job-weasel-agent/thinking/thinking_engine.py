from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field

from browser_use.llm.google.chat import ChatGoogle
from browser_use.llm.messages import UserMessage

from thinking.context import current_failure_count, current_goal, current_last_error, current_speed_mode, current_task_type
from thinking.steering_loader import SteeringLoader
from thinking.working_memory import WorkingMemory


class DeepThinkOutput(BaseModel):
    reasoning: str = Field(description="Structured reasoning about state/options/risks")
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


@dataclass
class ThinkContext:
    task: str
    goal: str | None
    task_type: str | None
    last_error: str | None
    failures: int
    speed_mode: str | None
    steering: str
    memory: str


class ThinkingEngine:
    """
    Multi-layer thinking system:
    - quick_think(): rule-based, cheap, runs every step
    - deep_think(): optional LLM call (flash-lite) only when needed
    """

    def __init__(self, memory: WorkingMemory, repo_root: str | None = None):
        self.memory = memory
        self.steering_loader = SteeringLoader(repo_root=repo_root)
        self._steering_cached: str | None = None

        self.deep_model_name = os.environ.get("WEASZEL_DEEP_THINK_MODEL", "gemini-2.5-flash-lite")
        self._deep_llm: ChatGoogle | None = None

    def steering_text(self) -> str:
        if self._steering_cached is not None:
            return self._steering_cached
        docs = self.steering_loader.load()
        self._steering_cached = self.steering_loader.extract_principles(docs)
        return self._steering_cached

    def should_deep_think(self, task: str) -> bool:
        if os.environ.get("WEASZEL_DEEP_THINK", "auto").lower() in ("0", "false", "off", "no"):
            return False
        mode = os.environ.get("WEASZEL_DEEP_THINK", "auto").lower()
        if mode in ("1", "true", "on", "yes"):
            return True

        # auto mode: deep-think only on anomalies or risky actions
        failures = current_failure_count.get()
        if failures >= 2:
            return True
        t = (task or "").lower()
        risky = any(k in t for k in ["pay", "checkout", "purchase", "buy now", "submit application", "delete", "remove", "confirm"])
        return risky

    def build_context(self, task: str) -> ThinkContext:
        steering = self.steering_text()
        memory_text = self.memory.to_prompt()
        return ThinkContext(
            task=task,
            goal=current_goal.get(),
            task_type=current_task_type.get(),
            last_error=current_last_error.get(),
            failures=current_failure_count.get(),
            speed_mode=current_speed_mode.get(),
            steering=steering,
            memory=memory_text,
        )

    def quick_think(self, ctx: ThinkContext) -> dict[str, Any]:
        """
        Cheap reasoning layer (no model call).
        Produces short, structured guidance for the action-selection model.
        """
        task = (ctx.task or "").strip()
        goal = ctx.goal or ""
        failures = ctx.failures
        last_error = ctx.last_error or ""

        risks: list[str] = []
        recs: list[str] = []
        if failures > 0:
            risks.append(f"Recent failures={failures}; avoid repeating same action blindly.")
            recs.append("If an element isn't found, re-check the page state and try alternative selectors or scroll.")
        if last_error:
            risks.append(f"Last error: {last_error[:200]}")
            recs.append("Mitigate the last error explicitly before attempting the next action.")

        t_lc = task.lower()
        if any(k in t_lc for k in ["checkout", "pay", "purchase", "buy"]):
            risks.append("Payment/checkout risk: do not submit irreversible actions without confirmation.")
            recs.append("Pause before final submit/payment; ask for confirmation.")

        # Efficiency guidance (from steering)
        recs.append("Prefer batching: do 2–5 straightforward actions in one step when safe.")
        recs.append("Use fallbacks: if blocked by login/captcha, switch approach or ask user.")

        return {
            "goal": goal,
            "task_type": ctx.task_type,
            "failures": failures,
            "risks": risks[:5],
            "recommendations": recs[:6],
        }

    async def deep_think(self, ctx: ThinkContext) -> DeepThinkOutput:
        if self._deep_llm is None:
            self._deep_llm = ChatGoogle(
                model=self.deep_model_name,
                api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.0,
            )

        prompt = f"""You are Weaszel's deep reasoning layer.

TASK:
{ctx.task}

CONTEXT:
- goal: {ctx.goal}
- task_type: {ctx.task_type}
- failures: {ctx.failures}
- last_error: {ctx.last_error}
- speed_mode: {ctx.speed_mode}

WORKING MEMORY (recent):
{ctx.memory or "(none)"}

STEERING PRINCIPLES (follow these):
{ctx.steering or "(none)"}

THINK:
1) State analysis: what is most likely happening / what might be missing?
2) Options: propose at least 2 approaches.
3) Risks: what could go wrong?
4) Best plan: concise recommendations for the next step.
Return JSON per the schema."""

        res = await self._deep_llm.ainvoke([UserMessage(content=prompt)], output_format=DeepThinkOutput)
        return res.completion



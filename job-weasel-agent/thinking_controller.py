from __future__ import annotations

import os
from typing import Any

from browser_use.agent.message_manager.views import HistoryItem
from browser_use.agent.service import Agent

from perf_context import current_step, current_task_id
from perf_logger import emit
from thinking_engine import ThinkingEngine


def _enabled() -> bool:
    return os.environ.get("WEASZEL_THINKING_MODE", "quick").lower() not in ("0", "off", "false", "no")


class ThinkingController:
    """
    Integrates ThinkingEngine into the Browser-Use loop via hooks.

    Strategy:
    - On step start: generate short pre-step thinking and inject as a system history item.
      This makes it visible to Browser-Use MessageManager's agent_history_description.
    - On step end: reflect and update working memory.
    """

    def __init__(self, engine: ThinkingEngine, task: str):
        self.engine = engine
        self.task = task

    def _get_state_hint(self, agent: Agent) -> str:
        # Best-effort: use cached browser summary if available, otherwise minimal.
        bs = getattr(agent.browser_session, "_cached_browser_state_summary", None)
        url = None
        title = None
        try:
            url = getattr(bs, "url", None) if bs else None
            title = getattr(bs, "title", None) if bs else None
        except Exception:
            pass
        return f"url={url or 'unknown'} title={title or 'unknown'}"

    def _get_outcome_hint(self, agent: Agent) -> str:
        last_output = getattr(agent.state, "last_model_output", None)
        last_result = getattr(agent.state, "last_result", None) or []
        parts = []
        if last_output is not None:
            ev = getattr(last_output, "evaluation_previous_goal", None)
            ng = getattr(last_output, "next_goal", None)
            if ev:
                parts.append(f"evaluation={ev}")
            if ng:
                parts.append(f"next_goal={ng}")
        errs = [getattr(r, "error", None) for r in last_result if getattr(r, "error", None)]
        if errs:
            parts.append(f"errors={errs[-1]}")
        return " | ".join(parts)[:900]

    async def on_step_start(self, agent: Agent) -> None:
        if not _enabled():
            return

        step = getattr(agent.state, "n_steps", 0)
        failures = getattr(agent.state, "consecutive_failures", 0)
        current_step.set(step)

        state_hint = self._get_state_hint(agent)
        out = await self.engine.pre_step_think(
            task=self.task,
            state_hint=state_hint,
            step=step,
            consecutive_failures=failures,
        )
        if out is None:
            return

        # Inject into agent history. MessageManager includes this as part of agent_history_description.
        try:
            mm = agent.message_manager
            snippet_lines = ["<weaszel_thinking>"]
            if out.reasoning:
                snippet_lines.append(out.reasoning.strip())
            if out.recommendations:
                snippet_lines.append("Recommendations:")
                snippet_lines.extend([f"- {r}" for r in out.recommendations[:6]])
            if out.risks:
                snippet_lines.append("Risks:")
                snippet_lines.extend([f"- {r}" for r in out.risks[:4]])
            snippet_lines.append("</weaszel_thinking>")
            snippet = "\n".join(snippet_lines)

            mm.state.agent_history_items.append(HistoryItem(system_message=snippet))
            # Keep history from bloating too much
            if len(mm.state.agent_history_items) > 50:
                mm.state.agent_history_items = mm.state.agent_history_items[-50:]

            emit("thinking.injected", task_id=current_task_id.get(), step=step)
        except Exception:
            return

    async def on_step_end(self, agent: Agent) -> None:
        if not _enabled():
            return

        step = getattr(agent.state, "n_steps", 0)
        last_result = getattr(agent.state, "last_result", None) or []
        had_error = any(getattr(r, "error", None) for r in last_result)
        outcome = self._get_outcome_hint(agent)
        await self.engine.post_step_reflect(task=self.task, outcome_hint=outcome, step=step, had_error=had_error)



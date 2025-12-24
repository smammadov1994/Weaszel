from __future__ import annotations

from typing import Any

from perf_context import current_step, current_task_id
from perf_logger import emit, span


class TimedLLM:
    """
    Lightweight wrapper that times LLM calls (ainvoke/invoke) and emits perf events.
    Works with Browser-Use BaseChatModel implementations (e.g., ChatGoogle).
    """

    def __init__(self, llm: Any):
        self._llm = llm

    def __getattr__(self, item: str) -> Any:
        # Delegate unknown attrs to the wrapped instance.
        return getattr(self._llm, item)

    @property
    def provider(self) -> str:
        return getattr(self._llm, "provider", "unknown")

    @property
    def model(self) -> str:
        return str(getattr(self._llm, "model", getattr(self._llm, "name", "unknown")))

    async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
        with span(
            "llm.ainvoke",
            provider=self.provider,
            model=self.model,
            task_id=current_task_id.get(),
            step=current_step.get(),
        ):
            result = await self._llm.ainvoke(*args, **kwargs)
        # Best-effort usage reporting (varies by provider)
        usage = getattr(result, "usage", None)
        if usage is not None:
            emit(
                "llm.usage",
                provider=self.provider,
                model=self.model,
                task_id=current_task_id.get(),
                step=current_step.get(),
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
                prompt_image_tokens=getattr(usage, "prompt_image_tokens", None),
                prompt_cached_tokens=getattr(usage, "prompt_cached_tokens", None),
            )
        return result

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        with span(
            "llm.invoke",
            provider=self.provider,
            model=self.model,
            task_id=current_task_id.get(),
            step=current_step.get(),
        ):
            return self._llm.invoke(*args, **kwargs)



import os
import asyncio
from typing import Optional
from browser_use import Agent, Browser, BrowserProfile, Controller
from browser_use.llm.google.chat import ChatGoogle
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from retry_controller import RetryController
from perf_context import current_task_id, current_step
from perf_logger import span, emit
from timed_llm import TimedLLM
from thinking_engine import ThinkingEngine
from thinking_controller import ThinkingController

console = Console()

class BrowserAgent:
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        headless: bool = False,
        task_type: str = "general",
        browser: Browser | None = None,
        speed_mode: str | None = None,
        persist_browser: bool = False,
    ):
        self.model_name = model_name
        self.headless = headless
        self.task_type = task_type
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Speed mode controls expensive defaults inside Browser-Use
        # safe (default Browser-Use profile), balanced (faster but still reliable), fast (aggressive)
        self.speed_mode = (speed_mode or os.environ.get("WEASZEL_SPEED_MODE", "balanced")).lower()
        self.persist_browser = persist_browser
        
        # Track tokens manually
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_tokens = 0
        
        # Initialize the LLM
        base_llm = ChatGoogle(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.0,
        )
        # Wrap for timing telemetry (thinking is integrated via step hooks, not by wrapping every LLM call)
        self.llm = TimedLLM(base_llm)
        
        # Initialize or reuse the Browser session (Browser-Use BrowserSession)
        if browser is not None:
            self.browser = browser
            self._owns_browser = False
        else:
            self._owns_browser = True
            # Key perf knobs from Browser-Use BrowserProfile defaults:
            # - interaction_highlight_duration defaults to 1.0s (can dominate perceived latency)
            # - minimum_wait_page_load_time defaults to 0.25s
            # - wait_for_network_idle_page_load_time defaults to 0.5s
            # - wait_between_actions defaults to 0.1s
            if self.speed_mode == "fast":
                highlight_elements = False
                interaction_highlight_duration = 0.0
                minimum_wait_page_load_time = 0.05
                wait_for_network_idle_page_load_time = 0.1
                wait_between_actions = 0.0
                enable_default_extensions = False
                cross_origin_iframes = False
                max_iframes = 20
            elif self.speed_mode == "safe":
                highlight_elements = True
                interaction_highlight_duration = 1.0
                minimum_wait_page_load_time = 0.25
                wait_for_network_idle_page_load_time = 0.5
                wait_between_actions = 0.1
                enable_default_extensions = True
                cross_origin_iframes = True
                max_iframes = 100
            else:  # balanced
                highlight_elements = False
                interaction_highlight_duration = 0.05
                minimum_wait_page_load_time = 0.1
                wait_for_network_idle_page_load_time = 0.2
                wait_between_actions = 0.0
                enable_default_extensions = True
                cross_origin_iframes = True
                max_iframes = 60

            # Image loading control:
            # We previously disabled images unconditionally for speed, which breaks image search UX.
            # Default is to keep images enabled unless explicitly disabled or in "fast" mode.
            disable_images = os.environ.get("WEASZEL_DISABLE_IMAGES", "0").lower() in ("1", "true", "yes", "on")
            if self.speed_mode == "fast":
                disable_images = True

            # Browser-Use's Browser is a BrowserSession. Not all BrowserProfile fields are accepted
            # as direct kwargs on BrowserSession.__init__ (version-dependent), so we pass speed knobs
            # via BrowserProfile for compatibility.
            profile = BrowserProfile(
                headless=self.headless,
                disable_security=True,
                # Critical for multi-turn workflows: keep the browser session alive after the agent returns `done`.
                # Browser-Use Agent.close() will only kill the browser when keep_alive is falsy.
                keep_alive=True if self.persist_browser else None,
                highlight_elements=highlight_elements,
                interaction_highlight_duration=interaction_highlight_duration,
                minimum_wait_page_load_time=minimum_wait_page_load_time,
                wait_for_network_idle_page_load_time=wait_for_network_idle_page_load_time,
                wait_between_actions=wait_between_actions,
                enable_default_extensions=enable_default_extensions,
                cross_origin_iframes=cross_origin_iframes,
                max_iframes=max_iframes,
                args=[
                    "--disable-infobars",
                    "--disable-popup-blocking",
                    "--disable-notifications",
                ],
            )
            if disable_images:
                profile.args.append("--blink-settings=imagesEnabled=false")
            self.browser = Browser(browser_profile=profile)
        
        # Initialize Controller
        self.controller = Controller()
        
        # Initialize Retry Controller
        self.retry_controller = None
    
    def _display_cost(self, num_steps: int = 0):
        """Display colorful cost breakdown"""
        # Gemini 2.5 Flash pricing per 1M tokens
        input_price = 0.30
        output_price = 2.50
        cache_price = 0.03
        
        # If we couldn't track tokens, estimate based on steps
        if self.total_input_tokens == 0 and self.total_output_tokens == 0 and num_steps > 0:
            # Rough estimate: ~1000 input tokens + ~300 output tokens per step
            self.total_input_tokens = num_steps * 1000
            self.total_output_tokens = num_steps * 300
            is_estimate = True
        else:
            is_estimate = False
        
        input_cost = (self.total_input_tokens / 1_000_000) * input_price
        output_cost = (self.total_output_tokens / 1_000_000) * output_price
        cache_cost = (self.total_cached_tokens / 1_000_000) * cache_price
        
        total_cost = input_cost + output_cost + cache_cost
        total_tokens = self.total_input_tokens + self.total_output_tokens
        
        # Create cost table
        cost_table = Table(show_header=False, box=None, padding=(0, 2))
        cost_table.add_column("Item", style="cyan")
        cost_table.add_column("Tokens", style="yellow", justify="right")
        cost_table.add_column("Cost", style="green", justify="right")
        
        estimate_mark = "~" if is_estimate else ""
        
        cost_table.add_row(
            "📥 Input",
            f"{estimate_mark}{self.total_input_tokens:,}",
            f"${input_cost:.6f}"
        )
        cost_table.add_row(
            "📤 Output",
            f"{estimate_mark}{self.total_output_tokens:,}",
            f"${output_cost:.6f}"
        )
        
        if self.total_cached_tokens > 0:
            cost_table.add_row(
                "💾 Cached",
                f"{self.total_cached_tokens:,}",
                f"${cache_cost:.6f}"
            )
        
        cost_table.add_row("", "", "")
        cost_table.add_row(
            "[bold]💰 Total Cost[/bold]",
            f"[bold]{estimate_mark}{total_tokens:,}[/bold]",
            f"[bold green]{estimate_mark}${total_cost:.6f}[/bold green]"
        )
        
        # Determine emoji based on cost
        if total_cost < 0.01:
            emoji = "🎉"
            message = "Practically free!"
        elif total_cost < 0.05:
            emoji = "✨"
            message = "Very affordable!"
        elif total_cost < 0.10:
            emoji = "👍"
            message = "Reasonable cost"
        else:
            emoji = "📊"
            message = "Complex task completed"
        
        if is_estimate:
            message += " (estimated)"
        
        console.print("\n")
        console.print(Panel(
            cost_table,
            title=f"{emoji} Task Cost - {message}",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        console.print()

    def run_sync(self, task: str):
        """Synchronous wrapper around async run method"""
        return asyncio.run(self.run(task))

    async def run(self, task: str) -> str:
        """
        Executes the given task using the browser agent with intelligent retry logic.
        """
        console.print(f"[bold cyan]🚀 Browser-Use Agent Starting...[/bold cyan]")
        console.print(f"[dim]Model: {self.model_name}[/dim]")

        # Ensure logs directory exists for Browser-Use conversation traces
        os.makedirs(os.path.abspath("logs"), exist_ok=True)

        task_id = os.environ.get("WEASZEL_TASK_ID") or None
        token_task = current_task_id.set(task_id)
        token_step = current_step.set(None)
        emit("task.start", task_id=task_id, model=self.model_name, speed_mode=self.speed_mode)
        
        # Agent settings: higher max_actions_per_step reduces LLM round-trips (big speed win)
        if self.speed_mode == "fast":
            max_actions_per_step = 6
            vision_detail_level = "low"
            llm_screenshot_size = (1024, 640)
            use_judge = False
            step_timeout = 90
        elif self.speed_mode == "safe":
            max_actions_per_step = 3
            vision_detail_level = "auto"
            llm_screenshot_size = None
            use_judge = True
            step_timeout = 180
        else:  # balanced
            max_actions_per_step = 5
            vision_detail_level = "low"
            llm_screenshot_size = (1200, 750)
            use_judge = False
            step_timeout = 120

        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser,
            controller=self.controller,
            use_vision=True,
            vision_detail_level=vision_detail_level,
            llm_screenshot_size=llm_screenshot_size,
            max_actions_per_step=max_actions_per_step,
            use_judge=use_judge,
            step_timeout=step_timeout,
            save_conversation_path="logs/conversation.json",
        )
        
        # Set default search engine to DuckDuckGo
        if hasattr(agent, 'browser_context') and hasattr(agent.browser_context, 'config'):
            agent.browser_context.config.default_search_engine = 'duckduckgo'

        try:
            # Initialize retry controller
            self.retry_controller = RetryController(
                llm=self.llm,
                browser_session=agent.browser_session,
                task_type=self.task_type
            )

            # Initialize thinking system (optional, gated by WEASZEL_THINKING_MODE)
            thinking_engine = None
            thinking_controller = None
            try:
                thinking_engine = ThinkingEngine()
                thinking_controller = ThinkingController(thinking_engine, task=task)
            except Exception:
                thinking_controller = None

            async def _on_step_start(a):
                # Compose multiple hooks
                await self.retry_controller.on_step_start(a)
                if thinking_controller is not None:
                    await thinking_controller.on_step_start(a)

            async def _on_step_end(a):
                await self.retry_controller.on_step_end(a)
                if thinking_controller is not None:
                    await thinking_controller.on_step_end(a)
            
            # Run agent with retry hooks
            with span("agent.run", task_id=task_id, speed_mode=self.speed_mode):
                history = await agent.run(
                    on_step_start=_on_step_start,
                    on_step_end=_on_step_end
                )
            
            # Track tokens from history - try multiple possible structures
            try:
                # Method 1: Direct history list
                if hasattr(history, 'history') and history.history:
                    for item in history.history:
                        if hasattr(item, 'result') and item.result:
                            if hasattr(item.result, 'usage') and item.result.usage:
                                usage = item.result.usage
                                self.total_input_tokens += getattr(usage, 'prompt_tokens', 0)
                                self.total_output_tokens += getattr(usage, 'completion_tokens', 0)
                                self.total_cached_tokens += getattr(usage, 'prompt_cached_tokens', 0) or 0
                
                # Method 2: Model results list
                elif hasattr(history, 'model_actions') and history.model_actions:
                    for action in history.model_actions:
                        if hasattr(action, 'result') and action.result:
                            if hasattr(action.result, 'usage') and action.result.usage:
                                usage = action.result.usage
                                self.total_input_tokens += getattr(usage, 'prompt_tokens', 0)
                                self.total_output_tokens += getattr(usage, 'completion_tokens', 0)
                                self.total_cached_tokens += getattr(usage, 'prompt_cached_tokens', 0) or 0
                
                # Method 3: Iterate through items
                elif hasattr(history, '__iter__'):
                    for item in history:
                        if hasattr(item, 'result') and item.result:
                            if hasattr(item.result, 'usage') and item.result.usage:
                                usage = item.result.usage
                                self.total_input_tokens += getattr(usage, 'prompt_tokens', 0)
                                self.total_output_tokens += getattr(usage, 'completion_tokens', 0)
                                self.total_cached_tokens += getattr(usage, 'prompt_cached_tokens', 0) or 0
            except Exception as e:
                console.print(f"[dim yellow]Note: Could not extract token usage ({e})[/dim yellow]")
            
            # Extract result
            result = history.final_result()
            
            # Count steps for cost estimation
            num_steps = len(history.history) if hasattr(history, 'history') else 0
            
            # Display cost
            self._display_cost(num_steps=num_steps)

            # Emit step metadata if available
            try:
                if hasattr(history, "history") and history.history:
                    for h in history.history:
                        md = getattr(h, "metadata", None)
                        if md is not None:
                            emit(
                                "history.step_metadata",
                                task_id=task_id,
                                step=md.step_number,
                                duration_s=md.duration_seconds,
                            )
            except Exception:
                pass
            
            if result:
                console.print(Panel(result, title="[bold green]✅ Task Completed[/bold green]", border_style="green"))
                return result
            else:
                console.print("[yellow]✅ Task finished but no specific result was returned.[/yellow]")
                return "Task completed."
                
        except Exception as e:
            console.print(f"[bold red]❌ Error during execution:[/bold red] {str(e)}")
            return f"Error: {str(e)}"
        finally:
            emit("task.end", task_id=task_id)
            current_step.reset(token_step)
            current_task_id.reset(token_task)
            if self._owns_browser and not self.persist_browser:
                await self.browser.stop()

    async def stop(self) -> None:
        """Stop the owned browser session (used when persist_browser=True)."""
        if self._owns_browser:
            await self.browser.stop()

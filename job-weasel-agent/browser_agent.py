import os
import asyncio
from typing import Optional
from browser_use import Agent, Browser, Controller, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from browser_use.llm.google.chat import ChatGoogle
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from retry_controller import RetryController

console = Console()

class BrowserAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash", headless: bool = False, task_type: str = "general"):
        self.model_name = model_name
        self.headless = headless
        self.task_type = task_type
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Track tokens manually
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_tokens = 0
        
        # Initialize the LLM
        self.llm = ChatGoogle(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.0,
        )
        
        # Initialize the Browser
        self.browser = Browser(
            config=BrowserConfig(
                headless=self.headless,
                disable_security=True,
                extra_chromium_args=[
                    "--disable-infobars",
                    "--disable-popup-blocking",
                    "--disable-notifications",
                ],
                new_context_config=BrowserContextConfig(
                    wait_for_network_idle_page_load_time=15.0, # Increased timeout for slower sites (e.g. Indeed)
                    minimum_wait_page_load_time=3.0, 
                )
            )
        )
        
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
        
        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser,
            controller=self.controller,
            use_vision=True,
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
            
            # Run agent with retry hooks
            history = await agent.run(
                on_step_start=self.retry_controller.on_step_start,
                on_step_end=self.retry_controller.on_step_end
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
            await self.browser.stop()

import os
import asyncio
from typing import Optional
from browser_use import Agent, Browser, Controller
from browser_use.llm.google.chat import ChatGoogle
from rich.console import Console
from rich.panel import Panel

console = Console()

class BrowserAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", headless: bool = False):
        self.model_name = model_name
        self.headless = headless
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the LLM
        # We use the standard Gemini models which work well with browser-use
        self.llm = ChatGoogle(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.0, # Low temperature for more deterministic actions
        )
        
        # Initialize the Browser
        self.browser = Browser(
            headless=self.headless,
            disable_security=True,
            args=[
                "--disable-infobars",
                "--disable-popup-blocking",
                "--disable-notifications",
            ]
        )
        
        # Initialize Controller (for custom tools if needed later)
        self.controller = Controller()

    async def run(self, task: str) -> str:
        """
        Executes the given task using the browser agent.
        """
        console.print(f"[bold cyan]🚀 Browser-Use Agent Starting...[/bold cyan]")
        console.print(f"[dim]Model: {self.model_name}[/dim]")
        
        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser,
            controller=self.controller,
            use_vision=True, # Gemini is multimodal, so we definitely want vision
            save_conversation_path="logs/conversation.json",
        )

        try:
            history = await agent.run()
            
            # Extract the final result
            result = history.final_result()
            
            if result:
                console.print(Panel(result, title="[bold green]Task Completed[/bold green]", border_style="green"))
                return result
            else:
                console.print("[yellow]Task finished but no specific result was returned.[/yellow]")
                return "Task completed."
                
        except Exception as e:
            console.print(f"[bold red]❌ Error during execution:[/bold red] {str(e)}")
            return f"Error: {str(e)}"
        finally:
            # Ensure browser is closed
            await self.browser.stop()

    def run_sync(self, task: str):
        """Synchronous wrapper for run"""
        return asyncio.run(self.run(task))

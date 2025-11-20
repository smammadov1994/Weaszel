import os
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from browser_use.llm.google.chat import ChatGoogle
from browser_use.agent.views import AgentStepInfo
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

@dataclass
class FailureTracker:
    """Track failures for escalating retry strategies"""
    failures_by_goal: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_failures: int = 0
    current_goal: str = ""
    last_successful_goal: str = ""
    consecutive_same_goal_failures: int = 0
    
class RetryController:
    """
    Intelligent retry controller with escalating strategies:
    - 5 failures on same step → Screenshot + replan
    - 10 failures on same step → Switch website
    - 15 total failures → Ask user for help
    """
    
    # Task-type specific website alternatives
    WEBSITE_ALTERNATIVES = {
        "flight_search": [
            "https://www.google.com/travel/flights",
            "https://www.kayak.com",
            "https://www.expedia.com/Flights",
            "https://www.skyscanner.com"
        ],
        "hotel_booking": [
            "https://www.booking.com",
            "https://www.hotels.com",
            "https://www.expedia.com/Hotels"
        ],
        "shopping": [
            "https://www.amazon.com",
            "https://www.walmart.com",
            "https://www.target.com"
        ],
    }
    
    def __init__(self, llm: ChatGoogle, browser_session, task_type: str = "general"):
        self.llm = llm
        self.browser_session = browser_session
        self.task_type = task_type
        self.tracker = FailureTracker()
        self.current_website_index = 0
        self.replanning_active = False
        
    def _normalize_goal(self, goal: str) -> str:
        """Normalize goal string for comparison"""
        # Remove common variations and focus on core action
        goal = goal.lower().strip()
        # Remove timestamps, indices, etc
        import re
        goal = re.sub(r'\d+', '', goal)
        return goal.strip()
    
    async def on_step_start(self, step_info: AgentStepInfo):
        """
        Called before each agent step.
        Monitor for repeated failures and trigger escalation.
        """
        # Extract current goal from step info
        if hasattr(step_info, 'next_goal') and step_info.next_goal:
            current_goal = self._normalize_goal(step_info.next_goal)
            
            # Update tracker
            if current_goal != self.tracker.current_goal:
                # New goal - reset consecutive failures but keep history
                self.tracker.last_successful_goal = self.tracker.current_goal
                self.tracker.current_goal = current_goal
                self.tracker.consecutive_same_goal_failures = 0
            
    async def on_step_end(self, step_info: AgentStepInfo):
        """
        Called after each agent step.
        Check if step failed and trigger appropriate escalation.
        """
        # Determine if step failed
        failed = self._check_if_failed(step_info)
        
        if failed:
            self.tracker.total_failures += 1
            self.tracker.consecutive_same_goal_failures += 1
            self.tracker.failures_by_goal[self.tracker.current_goal] += 1
            
            console.print(f"[dim]⚠️  Failure #{self.tracker.consecutive_same_goal_failures} on: {self.tracker.current_goal}[/dim]")
            
            # Check escalation thresholds
            if self.should_ask_user():
                await self._ask_user_intervention()
                return
            
            if self.should_switch_website():
                await self._switch_website()
                return
                
            if self.should_replan():
                await self._replan_with_screenshot()
                return
    
    def _check_if_failed(self, step_info: AgentStepInfo) -> bool:
        """
        Determine if a step failed based on evaluation.
        Look for failure keywords in evaluation_previous_goal.
        """
        if not hasattr(step_info, 'evaluation_previous_goal'):
            return False
            
        eval_text = step_info.evaluation_previous_goal or ""
        failure_keywords = ["failure", "failed", "error", "unsuccessful", "unable to"]
        
        return any(keyword in eval_text.lower() for keyword in failure_keywords)
    
    def should_replan(self) -> bool:
        """Trigger replanning after 5 consecutive failures on same goal"""
        return self.tracker.consecutive_same_goal_failures >= 5 and not self.replanning_active
    
    def should_switch_website(self) -> bool:
        """Switch website after 10 consecutive failures on same goal"""
        return self.tracker.consecutive_same_goal_failures >= 10
    
    def should_ask_user(self) -> bool:
        """Ask user for help after 15 total failures"""
        return self.tracker.total_failures >= 15
    
    async def _replan_with_screenshot(self):
        """
        Take screenshot, analyze with vision, and suggest alternative approaches.
        """
        console.print("\n[bold yellow]🤔 Hmm mode activated - Let me think about this differently...[/bold yellow]\n")
        
        try:
            # Take screenshot
            screenshot_path = await self.browser_session.save_screenshot()
            
            # Analyze with vision
            replan_prompt = f'''I'm trying to: {self.tracker.current_goal}

I've failed 5 times in a row. Looking at this screenshot, what am I missing?

Analyze:
1. Are there dropdowns, modals, or UI elements I need to interact with first?
2. Do I need to wait for something to load?
3. Are there pre-conditions I haven't met (login, selections, etc.)?
4. Am I clicking the wrong element?

Provide 3 specific alternative approaches I should try next.'''
            
            # Get alternative suggestions using ainvoke
            from browser_use.llm.messages import UserMessage
            response = await self.llm.ainvoke([UserMessage(content=replan_prompt)])
            suggestions = response.completion
            
            console.print(Panel(
                f"[bold cyan]Alternative Approaches:[/bold cyan]\n\n{suggestions}",
                title="🧠 Replanning",
                border_style="cyan"
            ))
            
            # Mark that we've replanned to avoid loop
            self.replanning_active = True
            
            # Reset consecutive failures to give it another chance
            self.tracker.consecutive_same_goal_failures = 0
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Replanning failed: {e}[/yellow]")
    
    async def _switch_website(self):
        """
        Switch to alternative website for the same task.
        """
        console.print("\n[bold yellow]🔄 Current approach not working. Switching to alternative website...[/bold yellow]\n")
        
        # Get alternative websites for this task type
        alternatives = self.WEBSITE_ALTERNATIVES.get(self.task_type, [])
        
        if not alternatives:
            console.print("[yellow]No alternative websites available for this task type.[/yellow]")
            return
        
        # Move to next website
        self.current_website_index = (self.current_website_index + 1) % len(alternatives)
        next_website = alternatives[self.current_website_index]
        
        console.print(f"[cyan]→ Switching to: {next_website}[/cyan]\n")
        
        try:
            # Navigate to new website
            await self.browser_session.navigate_to(next_website)
            
            # Reset failure counters for new site
            self.tracker.consecutive_same_goal_failures = 0
            self.replanning_active = False
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Website switch failed: {e}[/yellow]")
    
    async def _ask_user_intervention(self):
        """
        Pause execution and ask user for guidance after too many failures.
        """
        console.print("\n")
        console.print(Panel(
            f"[bold red]⏸️  I'm stuck after {self.tracker.total_failures} failed attempts.[/bold red]\n\n"
            f"[yellow]Current goal:[/yellow] {self.tracker.current_goal}\n\n"
            f"[dim]I've tried multiple approaches but keep running into issues.[/dim]",
            title="Need Your Help",
            border_style="red"
        ))
        
        console.print("\n[bold]What would you like me to do?[/bold]\n")
        console.print("  [cyan]1.[/cyan] Continue trying (5 more attempts)")
        console.print("  [cyan]2.[/cyan] Try a different approach (you describe)")
        console.print("  [cyan]3.[/cyan] Stop and show what I found so far")
        
        choice = Prompt.ask("\n▸ Choice", choices=["1", "2", "3"])
        
        if choice == "1":
            console.print("\n[green]✓ Continuing with 5 more attempts...[/green]\n")
            # Reset counters to give it another chance
            self.tracker.total_failures = 0
            self.tracker.consecutive_same_goal_failures = 0
            
        elif choice == "2":
            new_approach = Prompt.ask("\n[cyan]What should I try instead?[/cyan]")
            console.print(f"\n[green]✓ Trying new approach: {new_approach}[/green]\n")
            # Update the goal with user's suggestion
            self.tracker.current_goal = new_approach
            self.tracker.consecutive_same_goal_failures = 0
            
        elif choice == "3":
            console.print("\n[yellow]⏹️  Stopping execution...[/yellow]\n")
            # Trigger agent to stop (would need to integrate with agent's stop mechanism)
            raise KeyboardInterrupt("User requested stop")

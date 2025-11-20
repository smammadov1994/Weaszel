import os
import json
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from browser_use.llm.google.chat import ChatGoogle
from browser_use.llm.messages import UserMessage
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint

console = Console()

@dataclass
class QueryAnalysis:
    """Results of analyzing a user query"""
    task_type: str
    is_complete: bool
    missing_info: list[str]
    clarifying_questions: list[Dict[str, str]]
    confidence: float

class QueryPlanner:
    """
    Analyzes user queries and builds enhanced task instructions.
    
    This planner sits between user input and agent execution to:
    1. Identify incomplete or ambiguous queries
    2. Ask clarifying questions interactively
    3. Build comprehensive task instructions
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Use the same ChatGoogle client as browser_agent for consistency
        self.llm = ChatGoogle(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.0,
        )
    
    async def _analyze_query_async(self, query: str) -> QueryAnalysis:
        """Async version of analyze_query"""
        analysis_prompt = f"""You are an expert task analyzer for a browser automation agent.

Analyze this user query: "{query}"

IMPORTANT CONTEXT:
- The agent ALWAYS uses DuckDuckGo as the search engine (this is pre-configured)
- Do NOT ask which search engine to use
- Do NOT ask about Google vs DuckDuckGo vs other search engines

Determine:
1. What type of task is this? (flight_search, hotel_booking, shopping, job_search, research, image_search, form_filling, etc.)
2. Is this query complete and actionable, or does it need more information?
3. What critical information is missing that would make this task succeed?
4. What clarifying questions should we ask the user?

For each missing piece of information, create a specific question with:
- "key": a short identifier (e.g., "origin_city", "budget", "image_subject")
- "question": the question to ask the user
- "example": an example answer to help the user

CRITICAL RULES:
- Only ask for information that is TRULY MISSING from the query
- Do NOT ask about search engines (DuckDuckGo is always used)
- Do NOT ask optional details
- For image searches, only ask what KIND of image if not specified
- For flights, ask: origin, destination, dates
- For shopping, ask: what to buy, budget constraints
- For hotels, ask: location, dates, budget
- For job applications, ask: job title, location. NOTE: Always plan to Login first if credentials are likely needed.
- Avoid combining multiple search terms with "OR". Create sequential steps for different searches (e.g., "First search for X, then search for Y").

Return your analysis as a JSON object with this structure:
{{
  "task_type": "string",
  "is_complete": boolean,
  "missing_info": ["array", "of", "missing", "info"],
  "clarifying_questions": [
    {{"key": "identifier", "question": "Your question?", "example": "Example answer"}},
    ...
  ],
  "confidence": 0.0-1.0
}}

Respond with ONLY the JSON object, no other text."""

        try:
            # Use ChatGoogle .ainvoke() which is async
            response = await self.llm.ainvoke([UserMessage(content=analysis_prompt)])
            
            # Parse the JSON response
            response_text = response.completion.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis_data = json.loads(response_text)
            
            return QueryAnalysis(
                task_type=analysis_data.get("task_type", "unknown"),
                is_complete=analysis_data.get("is_complete", False),
                missing_info=analysis_data.get("missing_info", []),
                clarifying_questions=analysis_data.get("clarifying_questions", []),
                confidence=analysis_data.get("confidence", 0.5)
            )
            
        except Exception as e:
            console.print(f"[yellow]Warning: Query analysis failed ({e}). Proceeding with original query.[/yellow]")
            # Fallback: assume query is complete
            return QueryAnalysis(
                task_type="unknown",
                is_complete=True,
                missing_info=[],
                clarifying_questions=[],
                confidence=0.0
            )
    
    def ask_clarifications(self, analysis: QueryAnalysis) -> Dict[str, str]:
        """
        Interactively ask the user for missing information.
        
        Args:
            analysis: The QueryAnalysis object with questions to ask
            
        Returns:
            Dictionary mapping keys to user answers
        """
        if not analysis.clarifying_questions:
            return {}
        
        console.print("\n")
        console.print(Panel(
            "[bold cyan]🤔 I need more details to help you better![/bold cyan]",
            border_style="cyan"
        ))
        
        clarifications = {}
        
        for i, q in enumerate(analysis.clarifying_questions, 1):
            console.print(f"\n[bold]{i}. {q['question']}[/bold]")
            if q.get('example'):
                console.print(f"   [dim]Example: {q['example']}[/dim]")
            
            answer = Prompt.ask(f"   [cyan]▸[/cyan]")
            
            if answer.strip():
                clarifications[q['key']] = answer.strip()
        
        console.print()
        return clarifications
    
    async def _build_enhanced_task_async(self, original_query: str, clarifications: Dict[str, str]) -> str:
        """Async version of build_enhanced_task"""
        if not clarifications:
            return original_query
        
        enhancement_prompt = f"""You are an expert at creating detailed instructions for a browser automation agent.

Original user query: "{original_query}"

The user provided these additional details:
{json.dumps(clarifications, indent=2)}

Create a comprehensive, step-by-step task instruction that:
1. Specifies the exact website(s) to use (e.g., Google Flights, Amazon, LinkedIn).
2. **CRITICAL**: If the task involves applying, buying, posting, or searching for jobs, **Step 1 MUST be "Check if I am logged in. If not, log in."** (Use credentials from user data if available).
3. Includes all search parameters and filters from the clarifications.
4. **CRITICAL**: Do NOT use boolean "OR" operators in search queries (e.g., "React OR Python"). Instead, create **sequential** search steps: "First search for React, process results. Then clear search and search for Python, process results."
5. Defines what information to extract or action to take.
6. Specifies the output format.
7. Handles edge cases:
   - "If the page is blank or loading for >5s, reload the page."
   - "If 'Easy Apply' is not available, skip or save for later."
   - "If a captcha appears, try to solve it or switch to a different search engine/site."

The instruction should be clear, actionable, and complete.

Return ONLY the enhanced task instruction, no preamble or explanation."""

        try:
            # Use ChatGoogle .ainvoke() which is async
            response = await self.llm.ainvoke([UserMessage(content=enhancement_prompt)])
            
            enhanced_task = response.completion.strip()
            
            # Show the enhanced task to the user
            console.print(Panel(
                f"[bold green]Enhanced Task:[/bold green]\n\n{enhanced_task}",
                border_style="green"
            ))
            
            return enhanced_task
            
        except Exception as e:
            console.print(f"[yellow]Warning: Task enhancement failed ({e}). Using original query.[/yellow]")
            return original_query
    
    async def _plan_async(self, query: str) -> tuple[str, str]:
        """
        Async version of plan - runs all async operations in one event loop.
        This prevents "Event loop is closed" errors.
        """
        # Analyze the query
        console.print("[dim]🔍 Analyzing your request...[/dim]")
        analysis = await self._analyze_query_async(query)
        
        # If complete, return as-is
        if analysis.is_complete:
            console.print("[dim]✓ Query looks good! Proceeding...[/dim]\n")
            return (query, analysis.task_type)
        
        # Ask clarifying questions (this is sync, so it's fine)
        clarifications = self.ask_clarifications(analysis)
        
        if not clarifications:
            # User skipped questions, use original
            console.print("[dim]Using original query...[/dim]\n")
            return (query, analysis.task_type)
        
        # Build enhanced task
        console.print("[dim]🔨 Building enhanced task...[/dim]")
        enhanced_task = await self._build_enhanced_task_async(query, clarifications)
        
        return (enhanced_task, analysis.task_type)
    
    def plan(self, query: str) -> tuple[str, str]:
        """
        Main entry point: analyze, clarify, and enhance a query.
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple of (enhanced_query, task_type)
        """
        # Run all async operations in ONE event loop
        return asyncio.run(self._plan_async(query))

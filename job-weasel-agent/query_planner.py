import os
import json
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
import re
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

        # Session-level caches to avoid repeated analysis for identical queries
        # (Only safe when the query is already complete and we won't ask questions.)
        self._analysis_cache: dict[str, QueryAnalysis] = {}
        self._plan_cache: dict[str, tuple[str, str]] = {}
    
    async def _analyze_query_async(self, query: str) -> QueryAnalysis:
        """Async version of analyze_query"""
        cached = self._analysis_cache.get(query)
        if cached is not None:
            return cached

        query_lc = (query or "").lower()
        known_job_board = None
        if "indeed" in query_lc:
            known_job_board = "indeed"
        elif "linkedin" in query_lc:
            known_job_board = "linkedin"
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
- For job searches, ask: job title and location ONLY if missing. If the user already said a site (Indeed/LinkedIn), do NOT ask which job board to use.

EXTRA CONTEXT (already known from the query; do NOT ask for these again):
- job_board: {known_job_board or "unknown"}

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
            result = QueryAnalysis(
                task_type=analysis_data.get("task_type", "unknown"),
                is_complete=analysis_data.get("is_complete", False),
                missing_info=analysis_data.get("missing_info", []),
                clarifying_questions=analysis_data.get("clarifying_questions", []),
                confidence=analysis_data.get("confidence", 0.5)
            )

            # Post-filter: remove clarifying questions that are already answered by the query.
            # This guards against the model asking boilerplate (e.g., "Which job board?")
            # even when the user explicitly said "Indeed".
            if result.clarifying_questions:
                filtered_questions: list[Dict[str, str]] = []
                removed_keys: set[str] = set()

                for q in result.clarifying_questions:
                    question_text = (q.get("question") or "").lower()
                    key = (q.get("key") or "").lower()

                    # Job board already specified
                    if known_job_board and (
                        "job board" in question_text
                        or "jobboard" in key
                        or "job_board" in key
                        or "which site" in question_text
                        or "which website" in question_text
                        or "indeed" in question_text
                        or "linkedin" in question_text
                    ):
                        removed_keys.add(key or "job_board")
                        continue

                    # Job title already present (very simple heuristic)
                    # If query contains "software engineer" and the question is about job title, skip.
                    if ("software engineer" in query_lc or "engineer" in query_lc) and (
                        "job title" in question_text or "title" in question_text or "job_title" in key
                    ):
                        removed_keys.add(key or "job_title")
                        continue

                    filtered_questions.append(q)

                result.clarifying_questions = filtered_questions
                if removed_keys and result.missing_info:
                    # best-effort remove corresponding missing_info entries
                    mi = []
                    for item in result.missing_info:
                        item_lc = str(item).lower()
                        if any(k and k in item_lc for k in removed_keys):
                            continue
                        if known_job_board and ("job board" in item_lc or "jobboard" in item_lc):
                            continue
                        mi.append(item)
                    result.missing_info = mi

                # If we removed all clarifying questions, treat as complete.
                if not result.clarifying_questions:
                    result.is_complete = True

            # Cache analysis (safe; it doesn't include user-interactive answers)
            self._analysis_cache[query] = result
            return result
            
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
1. Specifies the exact website(s) to use (e.g., Google Flights, Amazon, LinkedIn)
2. Includes all search parameters and filters from the clarifications
3. Defines what information to extract or action to take
4. Specifies the output format (e.g., "list top 5 options with price, rating, link")
5. Handles edge cases (e.g., "if no results under budget, show closest options")

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
            # Global "definition of done" guardrails:
            # - Do NOT do extra actions beyond what the user explicitly asked.
            # - When the explicit goal is achieved, STOP and return a concise confirmation + ask what next.
            done_guard = (
                "\n\n<weaszel_done_policy>\n"
                "- Only perform actions required by the user's explicit request.\n"
                "- Do NOT apply extra filters, open extra pages, or continue exploring unless explicitly asked.\n"
                "- As soon as the explicit goal is achieved, STOP and return:\n"
                "  1) a short confirmation of completion\n"
                "  2) the current URL\n"
                "  3) a single follow-up question: \"What would you like to do next on this page?\"\n"
                "</weaszel_done_policy>\n"
            )

            # Job search fast path: If user asked only to search, do not apply filters unless asked.
            if analysis.task_type == "job_search":
                q = (query or "").strip()
                q_lc = q.lower()
                on_indeed = "indeed" in q_lc
                on_linkedin = "linkedin" in q_lc
                site = "Indeed" if on_indeed else ("LinkedIn Jobs" if on_linkedin else "Indeed")

                enhanced = (
                    f"Go to {site}.\n"
                    "Enter the job title and location as specified by the user query.\n"
                    "Click Search.\n"
                    "Wait until the job results list/grid is visible (not a blank page).\n"
                    "Then STOP. Do not click filters unless the user explicitly asked for filters.\n"
                    "Return: confirmation, current URL, and (optional) top 5 visible job titles + companies + links.\n"
                    + done_guard
                    + f"\n<original_user_request>\n{q}\n</original_user_request>"
                )
                console.print("[dim]✓ Query looks good! (Applied job-search strict completion policy)[/dim]\n")
                return (enhanced, analysis.task_type)

            # Small, high-leverage local templates to avoid UI-wrangling.
            # Image search: go directly to an images results view (avoids "click Images tab" + scrolling).
            if analysis.task_type == "image_search":
                q = (query or "").strip()
                q_lc = q.lower()
                # Heuristic to strip boilerplate phrasing
                q_lc = re.sub(r"^(please\s+)?(go\s+to\s+)?(google|duckduckgo|ddg)\s+(and\s+)?", "", q_lc).strip()
                q_lc = re.sub(r"^(search\s+for|search|find|look\s+for|show\s+me)\s+", "", q_lc).strip()
                q_lc = re.sub(r"^(a\s+)?(picture|photo|image|images|pics|pictures)\s+(of\s+)?", "", q_lc).strip()
                subject = q_lc.strip() or q

                enhanced = (
                    "Use DuckDuckGo Images (not web results).\n"
                    f"Search for: \"{subject}\".\n"
                    "Open the image results grid.\n"
                    "Return the top 5 images with: title (if present), source site, and direct link.\n"
                    "Avoid unnecessary scrolling; only scroll if the grid is not visible."
                )
                console.print("[dim]✓ Query looks good! (Applied image-search fast path)[/dim]\n")
                return (enhanced + done_guard + f"\n<original_user_request>\n{q}\n</original_user_request>", analysis.task_type)

            console.print("[dim]✓ Query looks good! Proceeding...[/dim]\n")
            return (query + done_guard, analysis.task_type)
        
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
        # If we previously planned this exact query and it was complete, reuse it
        cached = self._plan_cache.get(query)
        if cached is not None:
            return cached

        # Run all async operations in ONE event loop
        result = asyncio.run(self._plan_async(query))

        # Cache only if it did not require interactive clarifications
        # (i.e., enhanced_query == original query OR analysis says complete)
        try:
            analysis = self._analysis_cache.get(query)
            if analysis is not None and analysis.is_complete:
                self._plan_cache[query] = result
        except Exception:
            pass

        return result

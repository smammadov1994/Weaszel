import os
import sys
import time
import re
import uuid
import asyncio

# Add current directory to path so imports work - MUST BE BEFORE LOCAL IMPORTS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.status import Status
from dotenv import load_dotenv, set_key
from loguru import logger

# Load environment variables
# NOTE: We intentionally load from the *current working directory* because the installer
# and recommended run command `uv run python job-weasel-agent/weasel.py` are executed
# from the repo root.
load_dotenv(os.path.abspath(".env.local"))
load_dotenv()  # Also try .env just in case

# Configure Logging
logger.add("weasel.log", rotation="10 MB", level="DEBUG")

from legacy_agent import BrowserAgent as LegacyBrowserAgent
from browser_agent import BrowserAgent
from query_planner import QueryPlanner
from perf_logger import span, emit


console = Console()

PLAYWRIGHT_SCREEN_SIZE = (1440, 900)

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _looks_like_gibberish(s: str) -> bool:
    """
    Very lightweight gibberish heuristic so we can skip an LLM validation call
    for obvious non-tasks.
    """
    s = (s or "").strip()
    if not s:
        return True
    if len(s) < 2:
        return True
    # Mostly punctuation/symbols
    if re.fullmatch(r"[\W_]+", s):
        return True
    # No letters and very short -> likely not a task
    if not re.search(r"[A-Za-z]", s) and len(s) < 6:
        return True
    return False

def _looks_like_task(s: str) -> bool:
    """Heuristic: if it contains a verb-ish keyword or a URL, treat as a task."""
    s = (s or "").strip().lower()
    if not s:
        return False
    if "http://" in s or "https://" in s or ".com" in s or ".org" in s:
        return True
    verbs = [
        "find", "search", "go to", "open", "apply", "buy", "book", "compare",
        "research", "summarize", "shop", "look up", "check", "navigate",
    ]
    return any(v in s for v in verbs)

def load_user_data():
    """
    Load user profile data from a user-local file.

    Search order:
    1) ./user_data.md (repo root / current working directory)
    2) job-weasel-agent/user_data.md (legacy location next to this file)
    """
    candidates = [
        os.path.abspath("user_data.md"),
        os.path.join(os.path.dirname(__file__), "user_data.md"),
    ]
    for path in candidates:
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            continue
    return ""

def _sanitize_user_data_for_injection(user_data: str) -> str:
    """
    user_data.md in this repo historically contains BOTH:
    - personal profile info (useful)
    - procedural instructions (e.g., "apply filters", "rapid fire mode") that can
      override a user's explicit request and cause extra actions.

    For injection, we keep profile-like sections and strip procedural "process" sections.
    """
    if not user_data:
        return ""

    lines = user_data.splitlines()
    out: list[str] = []
    stop_at_headings = {
        "## application process",
        "## goal",
        "## application",
        "## process",
        "## rapid",
    }
    for line in lines:
        if line.strip().lower() in stop_at_headings:
            break
        out.append(line)

    cleaned = "\n".join(out).strip()
    # Also guard against very large injections
    return cleaned[:8000]

def _should_inject_profile(query: str, task_type: str) -> bool:
    """
    Only inject user profile data when it is likely needed.
    This prevents "profile instructions" from hijacking simple tasks like "search".
    """
    q = (query or "").lower()
    if any(k in q for k in ["use my info", "use my information", "my resume", "apply", "application", "fill out", "sign up"]):
        return True
    if task_type in {"form_filling", "job_application"}:
        return True
    return False

from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.console import Group

def print_welcome():
    console.clear()
    
    # ASCII Art - Display ABOVE the box
    weasel_art = """
⠀⠀⠀⠀⠀⠀⠀⠀⣠⡶⣛⣉⣙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⠋⠁⠀⠀⠀⠑⣿⣆⠀⢠⡤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⡴⠋⠑⣄⢤⡤⠧⣤⣬⣦⢤⣵⣤⣀⣠⢴⣶⡶⠶⠿⠿⣶⣶⣤⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⣘⣤⠿⠛⠛⠅⠀⠀⠀⠈⠉⠙⢿⣧⡀⠀⣀⣀⣀⠀⠙⢿⢹⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⣲⡟⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⡿⡍⠁⠀⠙⡗⠀⠈⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠊⣷⠋⠰⠒⠄⠀⠀⠀⠀⠀⠀⠀⡖⡆⠀⠀⠀⠀⠈⢇⢧⠀⠀⠀⠁⠀⢸⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠘⡇⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡎⣾⣛⠀⠀⢀⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣯⠇⡴⣫⣳⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡤⣄⠀⠀⠀⠀⠀⡇⡟⠃⠀⠀⡾⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡞⡎⣸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣯⣷⣷⠀⠀⠀⠀⡇⡧⠤⠶⠛⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢰⢱⠃⡿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⣼⡟⡷⣷⣯⡇⡇⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡤⣞⣉⡍⢏⡼⠀⠘⠷⠃⠁⣀⣀⣀⠀⠀⠀⠀⣇⢿⣿⡿⢼⡾⠁⠀⠀⠀⣿⣒⡲⠶⠦⠀⠀⠀⠀⠀
⠉⢁⠖⠉⢀⡜⣷⠀⠀⠀⠀⠀⠈⠉⠉⠀⠀⠀⠀⠛⠉⠙⠉⠉⠀⠀⠀⠀⣾⠳⢤⣄⠑⠦⡀⠀⠀⠀⠀
⠀⣎⡤⢺⠋⠀⠘⡧⡀⠀⠸⠤⠞⢧⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠟⡜⢹⡧⢄⡘⢌⠑⠦⣳⡀⠀
⠘⠁⢠⠃⠀⡠⠔⠉⠻⢷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠖⠡⠖⡡⠊⣿⠀⠀⠈⠳⠀⠀⠁⠀⠀
⠀⠀⠘⠛⠉⠀⠀⠀⠀⠀⠈⣷⣍⠛⠛⠭⠭⠭⠭⠟⢋⡥⠞⠁⠀⠀⠉⠀⠀⣷⣇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣯⠢⣝⠒⠒⠒⠒⡉⠉⠀⠀⠀⠀⠀⠀⠀⢀⠎⠀⠀⡏⢧⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡟⢆⡀⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠊⠁⠀⠀⠘⣼⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⣽⠇⠓⠤⠥⠭⠭⠭⠀⠀⠀⠀⠀⠀⠀⡆⠀⠀⠀⠀⡤⠊⢱⡘⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⣿⡶⣒⣶⡀⠀⠀⣠⡶⠶⠒⠒⠖⠋⠀⠀⠀⡀⠀⠀⠀⣀⠔⠻⡼⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡰⠁⣼⠃⠚⢁⣼⡇⠀⢰⣇⡒⠒⠂⠀⠀⠀⠀⠀⠀⣇⠀⠀⠀⠁⠀⠀⣸⣿⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠁⠀⠀⠈⣝⠇⠀⠀⢳⡄⠉⠁⠀⠀⠀⢀⡴⠓⠋⠀⠀⠀⠀⠀⠀⠀⠀⠘⣆
⠀⠀⠀⠀⠀⠀⠀⠀⠧⣀⣀⡠⠶⠋⠁⠀⠀⠀⠀⠉⠉⠙⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """
    
    # Print the weasel art centered
    console.print(Align.center(Text(weasel_art, style="bold magenta")))
    
    # Compact panel with just title and version
    subtitle = Text("🦊 Your AI Agent for the Web.", style="italic cyan")
    version_table = Table(show_header=False, box=None)
    version_table.add_row("[bold green]Version:[/bold green] 2.0.0", "[bold blue]Engine:[/bold blue] Browser-Use + Gemini 2.5 Flash")
    
    panel_content = Group(
        Align.center(subtitle),
        Text("\n"),
        Align.center(version_table)
    )
    
    console.print(Panel(
        panel_content,
        border_style="magenta",
        title="[bold white]WEASZEL[/bold white]",
        subtitle="[bold green]Ready to Hunt[/bold green]",
        padding=(1, 2)
    ))
    
    # Examples table BELOW the box
    console.print("\n")
    examples_table = Table(title="[bold white]Try asking me:[/bold white]", box=None, show_header=False)
    examples_table.add_row("🚀", "[cyan]Start rapid fire applications in NY[/cyan]")
    examples_table.add_row("🔍", "[cyan]Research the latest AI news on TechCrunch[/cyan]")
    examples_table.add_row("✈️", "[cyan]Find a cheap flight to Tokyo on Kayak[/cyan]")
    examples_table.add_row("🛒", "[cyan]Go to Amazon and find a mechanical keyboard[/cyan]")
    examples_table.add_row("🛑", "[red]Stop or Exit[/red]")
    
    console.print(Align.center(examples_table))
    console.print(Align.center(Text("\n[dim]Powered by Browser-Use + Gemini[/dim]")))
    if os.environ.get("EXPERIMENTAL_DESKTOP_ENABLED", "false").lower() == "true":
        console.print(Align.center(Text("⚠️  Experimental Desktop Control Enabled - Use with Caution", style="bold yellow")))
    console.print("\n")

from google import genai

def validate_query_with_gemini(query: str, api_key: str) -> bool:
    """
    Asks Gemini if the query makes sense.
    Returns True if valid, False otherwise.
    """
    # Fail fast on empty
    if not query or not query.strip():
        return False

    try:
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
        
        prompt = f"""
        You are a query validator for an AI agent.
        The user has input the following query: "{query}"
        
        Does this query make sense as a task for an AI agent to perform on a computer?
        It should be a clear instruction or question.
        
        Examples of INVALID queries:
        - "asdasd" (random gibberish)
        - "do" (incomplete command)
        - "nothing" (no action)
        - "hello" (just a greeting, not a task - though borderline, usually invalid for a task agent)
        - "" (empty)
        
        Examples of VALID queries:
        - "Find me a flight to Tokyo"
        - "Open notepad and write a poem"
        - "Check the weather"
        - "Go to google.com"
        
        Respond with ONLY "VALID" or "INVALID".
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        result = response.text.strip().upper()
        
        if "INVALID" in result:
            return False
        return True
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        # If validation fails (e.g. network), assume valid to not block user
        return True

def main():
    print_welcome()

    # Define env file path (keep consistent with load_dotenv above)
    env_file = os.path.abspath(".env.local")
    # Ensure runtime dirs exist (avoid failures when writing logs/artifacts)
    _ensure_dir(os.path.abspath("logs"))

    # Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[yellow]⚠️ GEMINI_API_KEY not found in environment.[/yellow]")
        console.print("Get your key here: [link=https://aistudio.google.com/app/apikey]https://aistudio.google.com/app/apikey[/link]")
        api_key = Prompt.ask("[bold green]Enter your Gemini API Key[/bold green]", password=True)
        
        # Save to .env.local for persistence
        with open(env_file, 'w') as f:
            f.write(f'GEMINI_API_KEY={api_key}\n')
        
        os.environ["GEMINI_API_KEY"] = api_key
        console.print("[green]✅ API key saved! You won't need to enter it again.[/green]")
    
    # Load User Data
    user_data = load_user_data()
    if user_data:
        console.print("[green]✅ User profile loaded from user_data.md[/green]")

    # Check for Experimental Desktop Flag
    desktop_enabled_str = os.environ.get("EXPERIMENTAL_DESKTOP_ENABLED")
    
    if desktop_enabled_str is None:
        console.print(Panel.fit(
            "[bold cyan]Welcome to Weaszel Setup![/bold cyan]\n\n"
            "Please select your operation mode:\n\n"
            "[bold green]1. Browser Automation (Recommended)[/bold green]\n"
            "   - Stable, fast, and safe.\n"
            "   - Best for web research, job applications, and data gathering.\n\n"
            "[bold yellow]2. Full Desktop Control (Experimental)[/bold yellow]\n"
            "   - Can control your mouse and keyboard.\n"
            "   - [red]Warning:[/red] Can be flaky and requires extra permissions.\n"
            "   - Use only if you need to control local apps (e.g. TextEdit, VS Code).",
            title="[bold magenta]Configuration[/bold magenta]"
        ))
        
        mode_choice = Prompt.ask("[bold]Select Mode[/bold]", choices=["1", "2"], default="1")
        
        if mode_choice == "2":
            # Desktop Mode Flow
            console.print("\n[bold yellow]⚠️  Enabling Experimental Desktop Control[/bold yellow]")
            console.print("You must grant [bold]Screen Recording[/bold] and [bold]Accessibility[/bold] permissions to your terminal.")
            console.print("1. Open System Settings -> Privacy & Security")
            console.print("2. Enable permissions for Terminal/iTerm/VSCode")
            console.print("3. Restart your terminal if needed.\n")
            
            if Prompt.ask("Are you ready to proceed?", choices=["y", "n"], default="y") == "y":
                set_key(env_file, "EXPERIMENTAL_DESKTOP_ENABLED", "true")
                os.environ["EXPERIMENTAL_DESKTOP_ENABLED"] = "true"
                console.print("[green]Desktop Control Enabled![/green]")
            else:
                set_key(env_file, "EXPERIMENTAL_DESKTOP_ENABLED", "false")
                os.environ["EXPERIMENTAL_DESKTOP_ENABLED"] = "false"
                console.print("[green]Falling back to Browser Mode.[/green]")
        else:
            # Browser Mode (Default)
            set_key(env_file, "EXPERIMENTAL_DESKTOP_ENABLED", "false")
            os.environ["EXPERIMENTAL_DESKTOP_ENABLED"] = "false"
            console.print("[green]Browser Automation Mode Configured![/green]")
    
    # Convert to boolean
    desktop_enabled = os.environ.get("EXPERIMENTAL_DESKTOP_ENABLED", "false").lower() == "true"
    
    if desktop_enabled:
        console.print("[bold yellow]⚠️  Experimental Desktop Control Active[/bold yellow]")

    # Main loop - ask for task first!
    browser_initialized = False
    browser_choice = None
    shared_browser_agent: BrowserAgent | None = None
    last_browser_context_hint: str | None = None
    
    while True:
        console.print("\n[bold cyan]What would you like me to do?[/bold cyan]")
        query = Prompt.ask("[bold magenta]>[/bold magenta]")

        if query.lower() in ['exit', 'quit']:
            break
            
        # Validate Query (fast local checks first; use Gemini only if unclear)
        if _looks_like_gibberish(query):
            is_valid = False
        elif _looks_like_task(query):
            is_valid = True
        else:
            with console.status("[bold green]🧠 Evaluating query...[/bold green]"):
                is_valid = validate_query_with_gemini(query, api_key)
            
        if not is_valid:
            console.print(Panel(f"[bold red]😕 I didn't understand that task.[/bold red]\n\nYour query [italic]'{query}'[/italic] doesn't seem like a clear instruction.\nPlease try again with a specific task like:\n- [cyan]\"Find a flight to Paris\"[/cyan]\n- [cyan]\"Open TextEdit and write a note\"[/cyan]", title="Invalid Query", border_style="red"))
            continue

        console.print(f"\n[bold]🚀 Starting Agent with task:[/bold] {query}")
        task_id = uuid.uuid4().hex[:12]
        os.environ["WEASZEL_TASK_ID"] = task_id
        emit("cli.task", task_id=task_id, query=query)

        try:
            # Lazy browser initialization - only when needed
            if not browser_initialized:
                # Ask Gemini if this task needs browser
                console.print("[dim]🤔 Analyzing if browser is needed...[/dim]")
                
                # Use Gemini to decide tool
                try:
                    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
                    tool_prompt = f"""
                    You are a tool selector for an AI agent.
                    The user wants to: "{query}"
                    
                    Does this task require a Web Browser to complete?
                    
                    Respond with "BROWSER" if it needs to visit websites, search the web, or use web apps.
                    Respond with "DESKTOP" if it is a local system task (opening apps, files, finder, settings, writing notes).
                    
                    Examples:
                    - "Find a flight" -> BROWSER
                    - "Open calculator" -> DESKTOP
                    - "Go to runescape.com" -> BROWSER
                    - "Search for cats" -> BROWSER
                    - "Open weaszel-screenshot.png" -> DESKTOP
                    
                    Response (BROWSER/DESKTOP):
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.0-flash-exp',
                        contents=tool_prompt
                    )
                    decision = response.text.strip().upper()
                    needs_browser = "BROWSER" in decision
                except Exception as e:
                    logger.error(f"Tool selection failed: {e}")
                    # Fallback to keyword heuristic if API fails
                    needs_browser = any(keyword in query.lower() for keyword in [
                        'search', 'google', 'website', 'amazon', 'indeed', 'linkedin',
                        'browse', 'find on', 'shop', 'buy', 'flight', 'kayak', 'book',
                        'go to', '.com', '.org', 'http'
                    ])
                
                # Enforce Desktop Flag
                if not needs_browser and not desktop_enabled:
                    console.print("[yellow]⚠️  Desktop Control is disabled.[/yellow]")
                    console.print("I can only perform browser tasks right now.")
                    console.print("To enable desktop control, delete [bold]EXPERIMENTAL_DESKTOP_ENABLED[/bold] from .env.local and restart.")
                    
                    # Force browser or ask again? Let's force browser as fallback or just continue loop
                    if Prompt.ask("Do you want to try this in the browser instead?", choices=["y", "n"]) == "y":
                        needs_browser = True
                    else:
                        continue

                if needs_browser:
                    # V2 Migration: Automatically use standard browser
                    console.print("[dim]🚀 Initializing browser...[/dim]")
                    browser_initialized = True
                else:
                    console.print("[dim]💻 No browser needed - using desktop tools only[/dim]")

            # Initialize Environment (only if browser was requested)
            if browser_initialized:
                # V2: Use Browser-Use Framework with Query Planner
                
                # Step 1: Plan the query (analyze, clarify, enhance)
                enhanced_query = query  # Default to original
                task_type = "general"  # Default task type
                try:
                    console.print("[dim]🧠 Planning your task...[/dim]")
                    planner = QueryPlanner()
                    with span("plan", task_id=task_id):
                        enhanced_query, task_type = planner.plan(query)
                    console.print("[green]✓ Planning complete![/green]\n")
                except Exception as e:
                    console.print(f"[yellow]⚠️  Query planner failed: {type(e).__name__}: {str(e)}[/yellow]")
                    console.print("[dim]→ Using original query instead...[/dim]\n")
                    # Print traceback for debugging
                    import traceback
                    logger.error(f"Query planner error: {traceback.format_exc()}")
                
                # Step 2: Execute with enhanced query and retry logic
                # Use gemini-2.5-flash - stable model optimized for agentic use cases
                # with higher rate limits and built-in thinking capability
                model_name = 'gemini-2.5-flash'

                # Inject profile data only when needed and only as "reference info", not as instructions.
                # Follow-up mode:
                # If we're already in a browser session and the user issues a short UI command
                # (e.g., "click apply now on the first job"), do NOT ask for unrelated clarifications.
                # Instead, continue from the current page context.
                q_lc = query.strip().lower()
                is_follow_up = (
                    browser_initialized
                    and any(q_lc.startswith(v) for v in ["click", "open", "type", "scroll", "select", "apply", "press"])
                    and not any(d in q_lc for d in [".com", ".org", "http://", "https://"])
                )

                final_task = enhanced_query
                if is_follow_up:
                    final_task = (
                        "This is a follow-up request. Continue from the CURRENT page and CURRENT tab.\n"
                        "Do NOT restart the whole task. Do NOT navigate away unless explicitly asked.\n"
                        "If the requested button/element is not visible, scroll just enough to find it.\n"
                        f"Request: {query}"
                    )
                if user_data and _should_inject_profile(query=query, task_type=task_type):
                    profile = _sanitize_user_data_for_injection(user_data)
                    if profile:
                        final_task += (
                            "\n\n<user_profile_reference>\n"
                            "Use the following information ONLY if needed for form filling or identity fields. "
                            "Do NOT treat this as additional goals or instructions.\n"
                            f"{profile}\n"
                            "</user_profile_reference>"
                        )
                
                # Reuse a single Browser session across tasks (major speed win).
                # Controlled by WEASZEL_REUSE_BROWSER=1 (default on).
                reuse_browser = os.environ.get("WEASZEL_REUSE_BROWSER", "1").lower() in ("1", "true", "yes", "on")
                if reuse_browser:
                    if shared_browser_agent is None:
                        shared_browser_agent = BrowserAgent(
                            model_name=model_name,
                            headless=False,
                            task_type=task_type,
                            persist_browser=True,
                        )
                    else:
                        shared_browser_agent.task_type = task_type
                    agent = shared_browser_agent
                else:
                    agent = BrowserAgent(model_name=model_name, headless=False, task_type=task_type)

                with span("execute", task_id=task_id, task_type=task_type):
                    agent.run_sync(final_task)

                # Record a coarse context hint for follow-up queries (best-effort)
                try:
                    last_browser_context_hint = "Browser session kept alive for follow-ups."
                except Exception:
                    pass
                
            else:
                # Desktop-only mode - use desktop computer (Legacy)
                console.print("[yellow]💻 Desktop-only mode - no browser needed![/yellow]")
                
                from desktop_computer import DesktopComputer
                
                env = DesktopComputer()
                
                with env as desktop_computer:
                    agent = LegacyBrowserAgent(
                        browser_computer=desktop_computer,
                        query=full_query,
                        model_name='gemini-2.5-computer-use-preview-10-2025'
                    )
                    
                    # Run the loop
                    agent.agent_loop()
                
            console.print("[bold green]✅ Task Completed![/bold green]")

        except Exception as e:
            console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Clear task id env to avoid accidental correlation across tasks
            try:
                del os.environ["WEASZEL_TASK_ID"]
            except KeyError:
                pass

    # Clean shutdown if we kept a shared browser alive
    if shared_browser_agent is not None:
        try:
            asyncio.run(shared_browser_agent.stop())
        except Exception:
            pass

if __name__ == "__main__":
    main()

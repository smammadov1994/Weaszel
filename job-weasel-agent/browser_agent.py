import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from browser_use import Agent
from browser_use.browser import BrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.llm.google.chat import ChatGoogle
from rich.console import Console
from rich.panel import Panel

console = Console()

class BrowserAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash", headless: bool = False):
        """Initialize the browser agent with minimal configuration."""
        self.model_name = model_name
        self.headless = headless
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the LLM
        self.llm = ChatGoogle(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.0,
        )
        
        # Initialize the Browser with persistence and anti-detection
        console.print(f"[yellow]🌐 Launching browser session...[/yellow]")
        profile = BrowserProfile(
            headless=self.headless, 
            keep_alive=True,  # Keep browser open for login pause
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
                "--disable-infobars",
                "--disable-popup-blocking",
                "--hide-scrollbars",
            ]
        )
        self.browser = BrowserSession(browser_profile=profile)
        
        # Create a custom controller with login pause capability
        from browser_use import Controller
        self.controller = Controller()
        
        # Flag to track if login was requested
        self._login_requested = False
        
        # Setup failure logging
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    def log_failure(self, context: str, error: str, action_attempted: str):
        """Log failures for learning and analysis."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = self.logs_dir / f"failure_{timestamp}.json"
        
        failure_data = {
            "timestamp": timestamp,
            "context": context,
            "error": error,
            "action_attempted": action_attempted
        }
        
        with open(log_file, 'w') as f:
            json.dump(failure_data, f, indent=2)
        
        console.print(f"[yellow]⚠️  Failure logged to {log_file}[/yellow]")
        
        @self.controller.action('Request user to login')
        def request_login(message: str = "Please log in to continue") -> str:
            """
            Use this action when you detect a login/sign-in page or requirement.
            This will pause the agent and wait for the user to complete the login process.
            """
            self._login_requested = True
            console.print(Panel(
                f"[yellow]{message}[/yellow]\n\n"
                "[cyan]You have two options:[/cyan]\n"
                "1. Log in to the site, then press [bold]Enter[/bold] to continue\n"
                "2. Type new instructions (e.g., 'go back to Indeed') and press [bold]Enter[/bold]\n\n"
                "[dim]The agent will either continue the current task or follow your new instructions.[/dim]",
                title="[bold red]🔐 Login Required[/bold red]",
                border_style="yellow"
            ))
            
            # Get user input - could be empty (just Enter) or new instructions
            user_input = input("\n[Your choice] ").strip()
            
            if user_input:
                # User provided new instructions
                console.print(f"\n[yellow]📝 New instructions received: {user_input}[/yellow]\n")
                self._login_requested = False
                return f"User cannot login to this site. User provided new instructions: '{user_input}'. IMMEDIATELY follow these new instructions. Forget the current job application and do what the user asked."
            else:
                # User just pressed Enter - continue with login
                console.print("\n[green]✓ Resuming task...[/green]\n")
                self._login_requested = False
                return "User has completed login. IMMEDIATELY VERIFY: 1) What tab/page am I currently on? Check the URL. 2) Is this the correct page for my task? 3) Do I need to switch tabs or navigate? 4) What is my current state (logged in, search terms, etc.)? Then continue."
        
        @self.controller.action("Request user guidance", param_model=None)
        def request_guidance(message: str = "I'm not sure how to proceed"):
            """Pause and ask user for guidance when confused or stuck."""
            console.print(Panel(
                f"[yellow]{message}[/yellow]\n\n"
                "[cyan]I need your help. Please provide guidance on how to proceed.[/cyan]\n"
                "[dim]Type your instructions and press Enter.[/dim]",
                title="[bold yellow]🤔 Agent Needs Guidance[/bold yellow]",
                border_style="yellow"
            ))
            
            # Get user guidance
            guidance = input("\n[Your guidance] ")
            console.print("\n[green]✓ Got it! Continuing with your guidance...[/green]\n")
            return f"User provided guidance: {guidance}. BEFORE proceeding, VERIFY: 1) What tab/page am I currently on? Check the URL. 2) Is this where I should be based on the guidance? 3) What is my current state? Then follow the user's instructions."
        
        @self.controller.action("Read JSON file")
        def read_json_file(file_path: str) -> str:
            """Read and return the contents of a JSON file from the local filesystem."""
            try:
                # Expand user path if needed
                expanded_path = os.path.expanduser(file_path)
                
                with open(expanded_path, 'r') as f:
                    data = json.load(f)
                
                console.print(f"[green]✓ Successfully read JSON file: {file_path}[/green]")
                # Return JSON as formatted string for the agent to use
                return f"File contents of {file_path}:\n{json.dumps(data, indent=2)}"
            except FileNotFoundError:
                return f"ERROR: File not found at path: {file_path}. Please verify the path is correct."
            except json.JSONDecodeError as e:
                return f"ERROR: Invalid JSON in file {file_path}: {str(e)}"
            except Exception as e:
                return f"ERROR reading file {file_path}: {str(e)}"


    async def run(self, task: str) -> str:
        """Execute the task using browser-use agent."""
        console.print(f"[bold cyan]🚀 Browser-Use Agent Starting...[/bold cyan]")
        console.print(f"[dim]Model: {self.model_name}[/dim]")
        
        # Add explicit instruction about login handling and task execution
        patient_task = (
            f"{task}\n\n"
            "CORE INTELLIGENCE PRINCIPLES:\n"
            "You are an intelligent browser agent. Your job is to understand the user's goal and accomplish it.\n"
            "\n"
            "REASONING TRACES (Chain-of-Thought):\n"
            "In your 'Thought' field, EXPLICITLY document your thinking:\n"
            "- What is the current state? (URL, page content, form state)\n"
            "- What is my goal right now?\n"
            "- Why am I choosing this action?\n"
            "- What do I expect to happen?\n"
            "Example: 'I am on Indeed job search page. Goal: Find React jobs. I see a search field. I will type \"Frontend engineer\" because that's the job title user wants. I expect search results to appear.'\n"
            "\n"
            "STATE TRACKING (Track Your Progress):\n"
            "In your memory, maintain an explicit state of progress:\n"
            "- Task: <user's original request>\n"
            "- Progress: <checklist of steps completed>\n"
            "- Current Step: <what I'm working on now>\n"
            "- Blockers: <anything preventing progress>\n"
            "Example Memory: 'Task: Apply to Frontend job | Progress: [✓] Navigated to Indeed, [✓] Searched for jobs, [ ] Click a job | Current: Looking at job listings | Blockers: None'\n"
            "\n"
            "DECISION-MAKING FRAMEWORK:\n"
            "Before EVERY action, ask yourself:\n"
            "1. What is my current goal?\n"
            "2. What do I see on the screen right now?\n"
            "3. What action will move me closer to the goal?\n"
            "4. How will I know if it worked?\n"
            "\n"
            "POST-ACTION VERIFICATION (CRITICAL):\n"
            "After EVERY action:\n"
            "1. Observe the result - look at the new screenshot carefully\n"
            "2. Did my action succeed? Be HONEST:\n"
            "   - If I typed text, is it visible in the field?\n"
            "   - If I clicked a button, did the page change as expected?\n"
            "   - If I scrolled, can I see new content?\n"
            "3. If NO → Why not? What should I try instead?\n"
            "4. Update my understanding of where I am AND update my state tracking\n"
            "\n"
            "TASK COMPLETION AWARENESS:\n"
            "Periodically ask yourself:\n"
            "- Have I accomplished what the user asked?\n"
            "- If YES → Report success and STOP\n"
            "- If NO → What's the next step?\n"
            "- If BLOCKED → Use 'Request user guidance'\n"
            "\n"
            "INTELLIGENT LOOP DETECTION:\n"
            "- Am I repeating the same action?\n"
            "- Has my situation changed in the last 3 steps?\n"
            "- Am I making progress toward the goal? (Check my state tracking)\n"
            "- If NO to any → STOP and use 'Request user guidance'\n"
            "\n"
            "ERROR RECOVERY STRATEGIES:\n"
            "When something fails, DON'T just retry blindly:\n"
            "1. Understand WHY it failed (wrong element? page not loaded? wrong page?)\n"
            "2. Consider alternatives:\n"
            "   - Different element to click?\n"
            "   - Need to wait longer?\n"
            "   - Wrong approach entirely?\n"
            "3. Try alternative OR ask user for guidance\n"
            "Example: If clicking 'Apply' opened external site I can't access → Don't retry → Instead use 'Request user to login' or go back and try different job\n"
            "\n"
            "JOB SEARCH INTELLIGENCE (If task involves job searching):\n"
            "- Understand user's goal: job title, preferred skills/tech, location, site\n"
            "- Navigate site's search interface naturally\n"
            "- Look for jobs matching criteria on current screen FIRST before scrolling\n"
            "- Prefer easy apply options (Easy Apply, Quick Apply, Apply Now)\n"
            "- If you scroll 2+ times without clicking a job, STOP and ask user\n"
            "- Read resume.json and identity.json for form filling\n"
            "- Use 'Request user to login' if you hit login pages or external sites you can't access\n"
            "\n"
            "OPERATIONAL ESSENTIALS:\n"
            "- Login: Use 'Request user to login' action (don't fill credentials yourself)\n"
            "- Files: Use 'Read JSON file' with /Users/seymurmammadov/Documents/Weaszel/resume.json or identity.json\n"
            "- Tabs: Switch to new tabs immediately when they open\n"
            "- Loops: If repeating same action 2+ times → STOP → Use 'Request user guidance'\n"
            "\n"
            "DOMAIN AWARENESS:\n"
            "- Pay attention to which website you're on (look at the URL).\n"
            "- If task started on indeed.com but you navigated to a different company site, that might be intentional.\n"
            "- However, if you can't find what you're looking for on the new site, use 'Request user guidance' to confirm this is correct.\n"
            "\n"
            "ANTI-LOOP PROTECTION:\n"
            "- If you find yourself doing the SAME action 2+ times in a row (like scrolling), STOP.\n"
            "- Scrolling more than twice in a row means you're stuck. Use 'Request user guidance'.\n"
            "- Use 'Request user guidance' action to explain what you're stuck on and ask for help.\n"
            "- Example: If you've scrolled 3 times without clicking a job, ask the user.\n"
            ""
        )
        
        # Create and run agent with patience settings and custom controller
        agent = Agent(
            task=patient_task,
            llm=self.llm,
            browser=self.browser,
            controller=self.controller,
            use_vision=True,
            max_steps=40,  # Increased from 30 to allow for more deliberate steps
            max_actions_per_step=2,  # Reduced from 3 to force deliberate, verified actions
        )
        
        result = await agent.run()
        return result.final_result()
    
    def run_sync(self, task: str):
        """Synchronous wrapper around async run method."""
        return asyncio.run(self.run(task))

import os
import asyncio
import json
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
            "Important instructions:\n"
            "- Take your time. Wait for pages to fully load before evaluating success or failure.\n"
            "- If you're unsure whether something worked, wait a few seconds and observe the page.\n"
            "- ALWAYS verify that each action succeeded before marking it as complete in your memory.\n"
            "- If you see a 'Sign in', 'Log in', or login page, immediately use the 'Request user to login' action.\n"
            "- Do NOT try to fill in login credentials yourself. Always use 'Request user to login' when authentication is needed.\n"
            "- When a new tab/window opens (like clicking 'Apply'), you MUST switch to that new tab to continue working there.\n"
            "- Never assume you've done something you haven't actually done yet. Check the page to verify.\n"
            "- To read data from local JSON files, use the 'Read JSON file' action:\n"
            "  * Resume data: /Users/seymurmammadov/Documents/Weaszel/resume.json\n"
            "  * Demographic info (gender, pronouns, disability, veteran status): /Users/seymurmammadov/Documents/Weaszel/identity.json\n"
            "\n"
            "INPUT VERIFICATION PROTOCOL (CRITICAL):\n"
            "- After EVERY input action (typing into a field), you MUST verify the text actually appeared.\n"
            "- In your NEXT step's Eval, explicitly check: 'Did the text I typed actually appear in the field?'\n"
            "- If you typed 'Frontend engineer' into a field, look at the page and confirm you can SEE 'Frontend engineer' in that field.\n"
            "- If the field is empty after typing, the action FAILED. Try again.\n"
            "- NEVER move on to the next action without verifying the previous input succeeded.\n"
            "- In your memory, track what you INTENDED to type vs what ACTUALLY appeared.\n"
            "- If you're moving fast and not seeing fields populate, SLOW DOWN and wait after each input.\n"
            "\n"
            "DELIBERATE PACING (MANDATORY):\n"
            "- After EVERY significant action (click, input, navigate), execute a 'wait' action for 2-3 seconds.\n"
            "- Use this wait time to let the page fully respond to your action.\n"
            "- During the wait, observe what happened. Did the action have the expected effect?\n"
            "- After the wait, in your NEXT step, reflect: 'What changed? Did my action succeed?'\n"
            "- NEVER rush. Quality > Speed. Taking 30 steps carefully is better than failing in 10 rushed steps.\n"
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
            "ANTI-LOOP PROTECTION:\n"
            "- If you find yourself doing the SAME action 2+ times in a row (like scrolling), STOP.\n"
            "- Scrolling more than twice in a row means you're stuck. Use 'Request user guidance'.\n"
            "- Use 'Request user guidance' action to explain what you're stuck on and ask for help.\n"
            "- Example: If you've scrolled 3 times without clicking a job, ask the user.\n"
            "\n"
            "DOMAIN AWARENESS:\n"
            "- Pay attention to which website you're on (look at the URL).\n"
            "- If task started on indeed.com but you navigated to a different company site, that might be intentional.\n"
            "- However, if you can't find what you're looking for on the new site, use 'Request user guidance' to confirm this is correct."
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

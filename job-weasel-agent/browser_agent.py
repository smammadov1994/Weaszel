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
                "[cyan]Please log in to the site manually in the browser.[/cyan]\n"
                "[dim]The agent will wait for you to complete the login.[/dim]",
                title="[bold red]🔐 Login Required[/bold red]",
                border_style="yellow"
            ))
            
            # Wait for user to press Enter
            input("\n[Press Enter to continue after logging in] ")
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
            "========================================\n"
            "IF YOUR TASK INVOLVES JOB SEARCHING OR APPLICATIONS, READ THIS SECTION:\n"
            "========================================\n"
            "\n"
            "JOB SEARCH UNDERSTANDING:\n"
            "- Understand the difference between JOB TITLE (what to search) and JOB PREFERENCES (what to filter).\n"
            "- If instructed to search for 'Frontend engineer' and 'focus on React/TypeScript jobs', DO:\n"
            "  * Search for: 'Frontend engineer' (in job title field)\n"
            "  * Filter by: Look at job descriptions and prefer ones mentioning React/TypeScript\n"
            "- Do NOT type comma-separated preferences into the job title search field.\n"
            "- Job titles are roles (e.g., 'Software Engineer', 'Frontend Developer', 'Data Analyst').\n"
            "- Preferences are skills/technologies (e.g., 'React', 'Python', 'AWS').\n"
            "\n"
            "ANTI-REFRESH RULES:\n"
            "- NEVER refresh the page unnecessarily. Before refreshing, ask yourself: 'Is the page broken or is the data I need already here?'\n"
            "- Do NOT use the 'go_back' action and then navigate forward - this causes unnecessary reloads.\n"
            "- Do NOT refresh just because you're unsure - instead, WAIT and observe the current page.\n"
            "- If the page looks correct and has content, DO NOT REFRESH IT.\n"
            "- Only refresh if: page is blank/broken, stuck loading, or explicitly shows an error.\n"
            "- After navigation, WAIT for the page to load, then work with what's there. Don't refresh.\n"
            "\n"
            "STATE VERIFICATION & SELF-REFLECTION PROTOCOL:\n"
            "- Every 3-5 steps, PAUSE and ask yourself these questions:\n"
            "  1. What was my original task? (re-read it from memory)\n"
            "  2. What key state/information do I need to maintain? (login status, form data, search terms, etc.)\n"
            "  3. Does the current page match what I expect based on my previous actions?\n"
            "  4. Have any critical conditions changed? (logged out, page refreshed, data cleared, etc.)\n"
            "  5. Am I making progress toward the goal, or am I stuck/looping?\n"
            "- In your MEMORY field, explicitly track critical state variables relevant to your task.\n"
            "- After ANY navigation (back, forward, tab switch, new page), re-verify your assumptions.\n"
            "- If something unexpected happened (form cleared, logged out, wrong page), ACKNOWLEDGE it and adapt.\n"
            "- Example memory: 'Task: Apply to jobs. State: Logged in=Yes, Search=[software engineer, NYC], Current=Job listing page'\n"
            "\n"
            "MANDATORY CHECKPOINTS (DO NOT SKIP):\n"
            "\n"
            "CHECKPOINT 1 - After Login:\n"
            "- Before proceeding, VERIFY search terms are in the fields.\n"
            "- Look at the job title field - does it show the title you were instructed to search for?\n"
            "- Look at the location field - does it show the location you were instructed to search for?\n"
            "- If EITHER field is EMPTY or WRONG, you MUST re-enter the search terms.\n"
            "- Do NOT click on any job until search is complete and verified.\n"
            "\n"
            "CHECKPOINT 2 - Before Applying to a Job:\n"
            "- Read the job title and description carefully.\n"
            "- Check if the job matches your tech stack preferences (e.g., React, TypeScript, JavaScript).\n"
            "- Look for keywords in the description that match your preferences.\n"
            "- If the job does NOT mention your preferred technologies, DO NOT APPLY.\n"
            "- Only click Apply on jobs that clearly match the requirements.\n"
            "- If unsure, use 'Request user guidance' to confirm the job is suitable.\n"
            "\n"
            "========================================\n"
            "END OF JOB-SPECIFIC INSTRUCTIONS\n"
            "========================================\n"
            "\n"
            "ANTI-LOOP PROTECTION:\n"
            "- If you find yourself doing the SAME action 3+ times in a row (like scrolling), STOP.\n"
            "- Use 'Request user guidance' action to explain what you're stuck on and ask for help.\n"
            "- Example: If you've scrolled 8 times and still can't find a button, ask the user.\n"
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

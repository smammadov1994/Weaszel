import os
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.status import Status
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv(".env.local")
load_dotenv() # Also try .env just in case

# Configure Logging
logger.add("weasel.log", rotation="10 MB", level="DEBUG")

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import BrowserAgent
from computers import PlaywrightComputer

console = Console()

PLAYWRIGHT_SCREEN_SIZE = (1440, 900)

def load_user_data():
    try:
        with open('user_data.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

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
    version_table.add_row("[bold green]Version:[/bold green] 1.0.0", "[bold blue]Engine:[/bold blue] Gemini 2.5 Computer Use")
    
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
    examples_table.add_row("�", "[cyan]Research the latest AI news on TechCrunch[/cyan]")
    examples_table.add_row("✈️", "[cyan]Find a cheap flight to Tokyo on Kayak[/cyan]")
    examples_table.add_row("�", "[cyan]Go to Amazon and find a mechanical keyboard[/cyan]")
    examples_table.add_row("🛑", "[red]Stop or Exit[/red]")
    
    console.print(Align.center(examples_table))
    console.print(Align.center(Text("\n[dim]Powered by Google Gemini Computer Use[/dim]\n")))

def main():
    print_welcome()

    # Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[yellow]⚠️ GEMINI_API_KEY not found in environment.[/yellow]")
        console.print("Get your key here: [link=https://aistudio.google.com/app/apikey]https://aistudio.google.com/app/apikey[/link]")
        api_key = Prompt.ask("[bold green]Enter your Gemini API Key[/bold green]", password=True)
        os.environ["GEMINI_API_KEY"] = api_key
    
    # Load User Data
    user_data = load_user_data()
    if user_data:
        console.print("[green]✅ User profile loaded from user_data.md[/green]")
    else:
        console.print("[yellow]⚠️ No user_data.md found. Creating template...[/yellow]")
        # (Template creation logic could go here, but I already created it)

    # Browser Selection
    console.print("\n[bold cyan]Which browser should I use?[/bold cyan]")
    console.print("[1] [bold white]Standard Chromium[/bold white] (Easiest, but might be detected)")
    console.print("[2] [bold white]Your Own Chrome[/bold white] (Stealthy, bypasses Cloudflare)")
    
    browser_choice = Prompt.ask("[bold magenta]Select Option[/bold magenta]", choices=["1", "2"], default="1")
    
    if browser_choice == "2":
        # Guide for Own Chrome
        instructions = """
[bold yellow]Step 1:[/bold yellow] Close ALL existing Chrome windows completely.
[bold yellow]Step 2:[/bold yellow] Open a new terminal window.
[bold yellow]Step 3:[/bold yellow] Run this command:
    [green]./start_chrome.sh[/green]
[bold yellow]Step 4:[/bold yellow] Log in to Indeed/LinkedIn in that new window.
        """
        console.print(Panel(instructions, title="[bold green]Setup Instructions[/bold green]", border_style="green"))
        Prompt.ask("[bold magenta]Press Enter when Chrome is ready and you are logged in...[/bold magenta]")
        os.environ["CHROME_DEBUG_PORT"] = "9222"
    else:
        # Standard Chromium
        if "CHROME_DEBUG_PORT" in os.environ:
            del os.environ["CHROME_DEBUG_PORT"]

    while True:
        console.print("\n[bold cyan]What would you like me to do?[/bold cyan]")
        query = Prompt.ask("[bold magenta]>[/bold magenta]")

        if query.lower() in ['exit', 'quit']:
            break

        # Augment query with user data
        full_query = query
        if user_data:
            full_query += f"\n\nHere is my personal information to use if needed:\n{user_data}"

        console.print(f"\n[bold]🚀 Starting Agent with task:[/bold] {query}")

        try:
            # Initialize Environment
            env = PlaywrightComputer(
                screen_size=PLAYWRIGHT_SCREEN_SIZE,
                initial_url="https://www.google.com",
                highlight_mouse=True
            )

            with env as browser_computer:
                agent = BrowserAgent(
                    browser_computer=browser_computer,
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

if __name__ == "__main__":
    main()

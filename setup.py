import os
import sys
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def check_ollama_status() -> bool:
    """Checks if Ollama is running locally on the default port."""
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def create_env_file(telegram_key: str, brave_key: str):
    """Writes the provided keys to a .env file."""
    env_content = f"""TELEGRAM_BOT_TOKEN={telegram_key}
BRAVE_SEARCH_API_KEY={brave_key}
"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "w") as f:
        f.write(env_content)
    console.print(f"\n[bold green]Success![/bold green] Configuration saved to {env_path}")

from src.branding import get_ascii_logo

def check_playwright() -> bool:
    """Checks if playwright browsers are installed."""
    try:
        import playwright
        return True
    except ImportError:
        return False

def main():
    logo = get_ascii_logo()
    console.print(logo, style="bold cyan")
    console.print(Panel.fit("[bold cyan]Welcome to the SILI: The Infinite Mind Upgrade[/bold cyan]", border_style="cyan"))
    
    # Check Ollama
    console.print("\n[yellow]Checking for local Ollama instance...[/yellow]")
    if check_ollama_status():
        console.print("[bold green]✓[/bold green] Ollama detected!")
    else:
        console.print("[bold red]![/bold red] Ollama not found on localhost:11434.")
        console.print("  Sili requires a local LLM. Please install Ollama from ollama.com.")
        Prompt.ask("Press Enter to continue setup regardless")

    # Check Playwright
    console.print("\n[yellow]Checking for Playwright...[/yellow]")
    if check_playwright():
        console.print("[bold green]✓[/bold green] Playwright environment detected!")
    else:
        console.print("[bold red]![/bold red] Playwright not found.")
        console.print("  Browser capabilities (Phase 14) will be disabled.")
        Prompt.ask("Press Enter to continue")

    console.print("\n[bold cyan]Cognitive Configuration[/bold cyan]")
    console.print("We need a few API keys to enable Sili's advanced features.")
    
    # Telegram Key
    console.print("\n[bold]1. Telegram Bot Token[/bold]")
    console.print("Required to control Sili via Telegram. Get one by messaging @BotFather on Telegram.")
    telegram_key = Prompt.ask("Enter your Telegram Bot Token (leave blank to skip)")
    
    # Brave Search Key
    console.print("\n[bold]2. Brave Search API Key[/bold]")
    console.print("Required for the agent to browse the web. You can get a free tier key from brave.com/search/api.")
    brave_key = Prompt.ask("Enter your Brave Search API Key (leave blank to skip)")

    if telegram_key or brave_key:
        create_env_file(telegram_key, brave_key)
        console.print("\n[bold green]Setup Complete![/bold green]")
        console.print("You can now start your Telegram bot by running: [yellow]python3 telegram_bot.py[/yellow]")
    else:
        console.print("\n[yellow]Setup finished without saving any keys.[/yellow] You can re-run this script later.")

if __name__ == "__main__":
    try:
        main()
    except EOFError:
        console.print("\n[bold red]Error:[/bold red] Interactive input is not available.")
        console.print("If you are running the one-line installer, try running it like this:")
        console.print("[yellow]bash -c \"$(curl -sSL https://raw.githubusercontent.com/silitheai/sili/main/install.sh)\"[/yellow]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user.[/yellow]")
        sys.exit(0)

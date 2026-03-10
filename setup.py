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

def main():
    console.print(Panel.fit("[bold cyan]Welcome to the Sili Setup Wizard[/bold cyan]", border_style="cyan"))
    
    # Check Ollama
    console.print("\n[yellow]Checking for local Ollama instance...[/yellow]")
    if check_ollama_status():
        console.print("[bold green]✓[/bold green] Ollama detected running on localhost:11434!")
    else:
        console.print("[bold red]![/bold red] Ollama does not appear to be running on localhost:11434.")
        console.print("  Make sure you have Ollama installed and running before using Sili.")
        Prompt.ask("Press Enter to continue setup regardless")

    console.print("\n[bold cyan]API Configuration[/bold cyan]")
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
    main()

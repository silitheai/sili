import os
import sys
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def check_ollama_status() -> list:
    """Checks if Ollama is running and returns a list of model names."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get("models", [])]
            return models
        return []
    except:
        return []

def create_env_file(telegram_key: str, user_id: str, brave_key: str, text_model: str, vision_model: str):
    """Writes the provided keys to a .env file."""
    env_content = f"""TELEGRAM_BOT_TOKEN={telegram_key}
TELEGRAM_USER_ID={user_id}
BRAVE_SEARCH_API_KEY={brave_key}
TEXT_MODEL={text_model}
VISION_MODEL={vision_model}
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

def get_input(prompt: str) -> str:
    """Gets input from the user, falling back to /dev/tty if stdin is redirected."""
    if sys.stdin.isatty():
        return Prompt.ask(prompt)
    else:
        try:
            # Try to open the controlling terminal for input
            with open('/dev/tty', 'r') as tty:
                console.print(prompt, end=" ")
                return tty.readline().strip()
        except:
            # If everything fails, raise EOFError to be caught by the main handler
            raise EOFError

def main():
    logo = get_ascii_logo()
    console.print(logo, style="bold cyan")
    console.print(Panel.fit("[bold cyan]Welcome to the SILI: The Infinite Mind Upgrade[/bold cyan]", border_style="cyan"))
    
    # Check for existing config
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        console.print("\n[yellow]⚠️ Existing configuration (.env) detected.[/yellow]")
        choice = get_input("Do you want to (O)verwrite, (K)eep existing and continue, or (E)xit? [O/K/E]").upper()
        if choice == 'K':
            console.print("[bold green]Keeping existing configuration. Setup complete![/bold green]")
            return
        elif choice == 'E':
            console.print("[yellow]Exiting setup.[/yellow]")
            sys.exit(0)
        # If O, continue to overwrite

    # Check Ollama
    console.print("\n[yellow]Checking for local Ollama instance...[/yellow]")
    detected_models = check_ollama_status()
    text_model = "llama3.1"
    vision_model = "llama3.2-vision"
    
    if detected_models:
        console.print("[bold green]✓[/bold green] Ollama detected!")
        console.print("\n[bold cyan]Ollama Model Selection[/bold cyan]")
        
        # Text Model Selection
        console.print("\nSelect your [bold]Text Reasoning Model[/bold]:")
        for i, m in enumerate(detected_models):
            console.print(f"  {i+1}. {m}")
        
        while True:
            choice = get_input(f"Pick a number (default: llama3.1)")
            if not choice:
                text_model = "llama3.1"
                break
            if choice.isdigit() and 1 <= int(choice) <= len(detected_models):
                text_model = detected_models[int(choice)-1]
                break
            console.print("[red]Invalid choice.[/red]")

        # Vision Model Selection
        console.print("\nSelect your [bold]Vision/Multimodal Model[/bold]:")
        for i, m in enumerate(detected_models):
            console.print(f"  {i+1}. {m}")
        
        while True:
            choice = get_input(f"Pick a number (default: llama3.2-vision)")
            if not choice:
                vision_model = "llama3.2-vision"
                break
            if choice.isdigit() and 1 <= int(choice) <= len(detected_models):
                vision_model = detected_models[int(choice)-1]
                break
            console.print("[red]Invalid choice.[/red]")
            
        console.print(f"\n[green]Models selected:[/green] Text: {text_model} | Vision: {vision_model}")
    else:
        console.print("[bold red]![/bold red] Ollama not found on localhost:11434.")
        console.print("  Sili requires a local LLM. Please install Ollama from ollama.com.")
        get_input("Press Enter to continue setup regardless")

    # Check Playwright
    console.print("\n[yellow]Checking for Playwright...[/yellow]")
    if check_playwright():
        console.print("[bold green]✓[/bold green] Playwright environment detected!")
    else:
        console.print("[bold red]![/bold red] Playwright not found.")
        console.print("  Browser capabilities (Phase 14) will be disabled.")
        get_input("Press Enter to continue")

    console.print("\n[bold cyan]Cognitive & Security Configuration[/bold cyan]")
    console.print("We need a few API keys and security details to link Sili to your identity.")
    
    # Telegram Key
    console.print("\n[bold]1. Telegram Bot Token[/bold]")
    console.print("Required to control Sili via Telegram. Get one by messaging @BotFather.")
    telegram_key = get_input("Enter your Telegram Bot Token")
    
    # Telegram User ID
    console.print("\n[bold]2. Telegram User ID[/bold]")
    console.print("Sili will ONLY respond to you. Message @userinfobot to get your ID (It must be a number).")
    while True:
        user_id = get_input("Enter your Telegram User ID")
        if user_id.isdigit():
            break
        console.print("[bold red]Invalid ID![/bold red] Your Telegram User ID must be a numeric string (e.g., 12345678).")

    # Pairing Code Flow (Optional but recommended)
    console.print("\n[bold]3. Security Pairing[/bold]")
    console.print("Once you start the bot, it will send you a pairing code to verify this link.")
    
    # Brave Search Key
    console.print("\n[bold]4. Brave Search API Key[/bold]")
    console.print("Required for the agent to browse the web.")
    brave_key = get_input("Enter your Brave Search API Key (leave blank to skip)")

    if telegram_key and user_id:
        create_env_file(telegram_key, user_id, brave_key, text_model, vision_model)
        console.print("\n[bold green]Setup Complete![/bold green]")
        console.print("You can now start your Telegram bot by running: [yellow]python3 telegram_bot.py[/yellow]")
        console.print("[dim]Note: On first message, Sili will ask for a final pairing verification.[/dim]")
    else:
        console.print("\n[bold red]Error:[/bold red] Telegram Token and User ID are required for Sili to function.")
        sys.exit(1)

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

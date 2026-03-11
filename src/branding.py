
def get_ascii_logo():
    """Returns the SILI ASCII logo for terminal branding."""
    return r"""
    ▒███████▒ ██▓ ██▓     ██▓
    ▒ ▒ ▒ ▄▀░▓██▒▓██▒    ▓██▒
    ░ ▒ ▄▀▒ ░▒██▒▒██░    ▒██▒
      ▄▀▒   ░░██░▒██░    ░██░
    ▒███████▒░██░░██████▒░██░
    ░▒▒ ▓  ▒ ░▓  ░ ▒░▓  ░░▓  
    ░░▒ ▒  ░  ▒ ░░ ░ ▒  ░ ▒ ░
    ░ ░ ░  ░  ▒ ░  ░ ░    ▒ ░
      ░       ░      ░  ░ ░  
      ░                      
    [ SILI: THE INFINITE MIND ]
    """

def print_banner():
    """Prints the SILI banner to the console."""
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    logo = get_ascii_logo()
    console.print(Panel(logo, style="bold cyan", expand=False))

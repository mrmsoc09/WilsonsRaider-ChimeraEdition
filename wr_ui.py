from rich.console import Console
from rich.theme import Theme
from branding import Brand

# Custom color theme based on user request
custom_theme = Theme({
    "info": "green",
    "success": "bold green",
    "warning": "orange3",
    "danger": "bold red",
    "header": "bold gold1",
    "highlight": "bold white",
    "purple_action": "bold purple",
    "default": "white"
})

console = Console(theme=custom_theme, style="default on black")

def print_banner():
    console.print(f"[header]=====================================================[/header]")
    console.print(f"[header]      {Brand.TOOL_NAME}      [/header]")
    console.print(f"[header]=====================================================[/header]")

def print_header(text):
    console.print(f"\n[header]>>> {text}[/header]")

def print_info(text):
    console.print(f"[info]    - {text}[/info]")

def print_success(text):
    console.print(f"[success]  [+] {text}[/success]")

def print_warning(text):
    console.print(f"[warning]  [!] {text}[/warning]")

def print_danger(text):
    console.print(f"[danger] [!!!] {text}[/danger]")

def print_purple(text):
    console.print(f"[purple_action]  [*] {text}[/purple_action]")

def print_highlight(text):
    console.print(f"[highlight]{text}[/highlight]")

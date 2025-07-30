import rich
from rich.console import Console
from rich.theme import Theme
from .branding import THEME, get_name

console = Console(theme=THEME)

def print_banner():
    tool_name = get_name('tool')
    console.print(f"\n[[banner]]{tool_name}[/banner]]", justify="center")
    console.print("[info]------------------------------------------------------------[/info]", justify="center")

def print_header(text):
    console.print(f"\n[header]--- {text} ---[/header]")

def print_subheader(text):
    console.print(f"[subheader]{text}[/subheader]")

def print_info(text):
    console.print(f"[info][>] {text}[/info]")

def print_success(text):
    console.print(f"[success][+] {text}[/success]")

def print_warning(text):
    console.print(f"[warning][!] {text}[/warning]")

def print_error(text):
    console.print(f"[error][X] {text}[/error]")

def print_vulnerability(vuln):
    severity_style = f"vulnerability.{vuln.severity.lower()}"
    console.print(f"[{severity_style}]Found: {vuln.name} ({vuln.severity}) on {vuln.asset.name}[/{severity_style}]")

def print_purple_team_header(finding_name):
    console.print(f"\n[header]Purple Team Simulation for: {finding_name}[/header]")

def print_red_team(text, success=True):
    prefix = "[+]" if success else "[!" + "]"
    console.print(f"[red_team]{prefix} [Red Team] {text}[/red_team]")

def print_blue_team(text):
    console.print(f"[blue_team][+] [Blue Team] {text}[/blue_team]")

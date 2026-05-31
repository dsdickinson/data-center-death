from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from datetime import datetime

console = Console()

def clear_screen():
    """Clear the terminal screen"""
    console.clear()

def print_banner():
    """Display game title banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                   DATA CENTER DEATH                       ║
    ║              A Game of Power, Heat & Decisions            ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def print_status(game_state):
    """Display current game status"""
    console.print("\n")
    
    # Create status panel
    status_text = f"""
    Day {game_state.day} | Money: ${game_state.money:,.0f} | Reputation: {game_state.reputation:.1f}/100
    Location: {game_state.current_datacenter.upper()}
    System Health: {game_state.get_total_health():.1f}% | Power Draw: {game_state.get_power_draw():.1f} MW
    Hosted Clients: {game_state.hosted_clients} | Daily Revenue: ${game_state.monthly_revenue:,.0f}
    """
    console.print(Panel(status_text.strip(), title="[bold]Status[/bold]", border_style="blue"))

def print_infrastructure(game_state):
    """Display infrastructure status"""
    table = Table(title="[bold]Infrastructure Status[/bold]", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="green")
    table.add_column("Count", justify="center")
    table.add_column("Avg Health", justify="center")
    table.add_column("Status", justify="center")
    
    components = [
        ("Servers", game_state.servers),
        ("Cooling Units", game_state.cooling_units),
        ("Power Units", game_state.power_units),
        ("Switches", game_state.switches),
    ]
    
    for comp_name, comp_list in components:
        count = len(comp_list)
        avg_health = sum(hw.health for hw in comp_list) / len(comp_list) if comp_list else 0
        
        if avg_health > 80:
            status = "✓ Healthy"
            color = "green"
        elif avg_health > 50:
            status = "⚠ Degraded"
            color = "yellow"
        else:
            status = "✗ Critical"
            color = "red"
        
        table.add_row(comp_name, str(count), f"{avg_health:.1f}%", f"[{color}]{status}[/{color}]")
    
    console.print(table)

def print_incidents(game_state):
    """Display active incidents"""
    if game_state.active_incidents:
        console.print("\n[bold red]⚠️  ACTIVE INCIDENTS:[/bold red]")
        for i, incident in enumerate(game_state.active_incidents, 1):
            console.print(f"  {i}. {incident}")

def print_menu(title: str, options: dict):
    """Display a menu with options"""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    for key, description in options.items():
        console.print(f"  [{key}] {description}")
    console.print()

def print_message(message: str, style: str = ""):
    """Print a styled message"""
    console.print(message, style=style)

def get_input(prompt: str = "> ") -> str:
    """Get user input"""
    return console.input(f"[bold cyan]{prompt}[/bold cyan]").strip().lower()

def show_datacenter_choice():
    """Show datacenter selection screen"""
    clear_screen()
    print_banner()
    
    console.print("\n[bold]Welcome to Data Center Death![/bold]")
    console.print("Choose your starting location:\n")
    
    from game_state import DATA_CENTER_LOCATIONS
    
    # Create numbered options for all data centers
    options = {}
    location_keys = list(DATA_CENTER_LOCATIONS.keys())
    location_map = {}
    
    for i, key in enumerate(location_keys, 1):
        dc = DATA_CENTER_LOCATIONS[key]
        options[str(i)] = f"{dc.name} - {dc.location} (Power: {dc.power_capacity}MW, Cost: ${dc.base_cost:,.0f}/mo)"
        location_map[str(i)] = key
    
    print_menu("Data Centers", options)
    
    # Keep asking until valid selection
    while True:
        choice = get_input(f"Select datacenter (1-{len(location_keys)}): ")
        if choice in location_map:
            return location_map[choice]
        console.print("[red]Invalid selection. Please enter a valid number.[/red]")

def show_main_menu(game_state):
    """Show main game menu"""
    clear_screen()
    print_banner()
    print_status(game_state)
    print_infrastructure(game_state)
    print_incidents(game_state)
    
    options = {
        "S": "Show statistics (detailed view)",
        "U": "Upgrade infrastructure",
        "M": "Manage clients & revenue",
        "R": "Respond to incidents",
        "A": "Advance one day",
        "Q": "Quit game",
    }
    
    print_menu("Main Menu", options)
    return get_input("Choose action: ")

def show_statistics(game_state):
    """Show detailed statistics"""
    clear_screen()
    print_banner()
    
    console.print(f"\n[bold]Day {game_state.day} Statistics[/bold]\n")
    
    dc = game_state.current_datacenter
    console.print(f"Location: {dc}")
    console.print(f"Capital: ${game_state.money:,.0f}")
    console.print(f"Reputation: {game_state.reputation:.1f}/100")
    console.print(f"Clients: {game_state.hosted_clients}")
    console.print(f"Daily Revenue: ${game_state.monthly_revenue:,.0f}")
    
    console.print("\n[bold]Hardware Details:[/bold]")
    
    for category, items in [
        ("Servers", game_state.servers),
        ("Cooling", game_state.cooling_units),
        ("Power", game_state.power_units),
        ("Network", game_state.switches),
    ]:
        console.print(f"\n  {category}:")
        for item in items:
            status = "✓" if item.health > 50 else "✗"
            console.print(f"    {status} {item.name}: {item.health:.1f}% health, {item.power_draw}W")
    
    get_input("Press enter to continue...")

def show_upgrade_menu(game_state):
    """Show upgrade options"""
    clear_screen()
    print_banner()
    print_status(game_state)
    
    console.print("\n[bold]Upgrade Infrastructure[/bold]\n")
    
    options = {
        "1": "Add Server ($50,000)",
        "2": "Add Cooling Unit ($40,000)",
        "3": "Repair failing hardware ($15,000/unit)",
        "4": "Upgrade UPS capacity ($75,000)",
        "B": "Back to main menu",
    }
    
    print_menu("Upgrades", options)
    return get_input("Select upgrade: ")

def show_clients_menu(game_state):
    """Show client management menu"""
    clear_screen()
    print_banner()
    print_status(game_state)
    
    console.print("\n[bold]Manage Clients[/bold]\n")
    console.print(f"Current clients: {game_state.hosted_clients}")
    console.print(f"Available capacity: {100 - (len(game_state.servers) * 20)}% slots\n")
    
    options = {
        "A": "Acquire new clients (+1 client, $20,000 marketing)",
        "P": "Poach competitors' clients (+3 clients, $100,000, -10 reputation)",
        "B": "Back to main menu",
    }
    
    print_menu("Clients", options)
    return get_input("Choose action: ")

def show_incidents_menu(game_state):
    """Show incident response menu"""
    clear_screen()
    print_banner()
    print_status(game_state)
    
    if not game_state.active_incidents:
        console.print("\n[bold green]✓ No active incidents![/bold green]")
        get_input("Press enter to continue...")
        return None
    
    console.print("\n[bold red]Active Incidents:[/bold red]\n")
    for i, incident in enumerate(game_state.active_incidents, 1):
        console.print(f"{i}. {incident}")
    
    options = {
        "1": "Quick fix ($5,000, 70% success rate)",
        "2": "Professional repair ($15,000, 95% success rate)",
        "3": "Ignore (risky, may escalate)",
        "B": "Back to main menu",
    }
    
    print_menu("Incident Response", options)
    return get_input("Choose action: ")

import random
from game_state import GameState, DATA_CENTER_LOCATIONS, Hardware
from ui import (
    show_datacenter_choice, show_main_menu, show_statistics, 
    show_upgrade_menu, show_clients_menu, show_incidents_menu,
    print_message, clear_screen, print_banner
)

class Game:
    def __init__(self):
        self.state = GameState()
        self.running = True
    
    def initialize_game(self):
        """Setup new game"""
        datacenter = show_datacenter_choice()
        self.state.current_datacenter = datacenter
        
        dc = DATA_CENTER_LOCATIONS[datacenter]
        print_message(f"\n✓ Starting at {dc.name}", style="bold green")
        print_message(f"  Location: {dc.location}")
        print_message(f"  Power Capacity: {dc.power_capacity}MW")
        print_message(f"  Cooling: {dc.cooling_capacity} tons/hr")
        print_message(f"  Climate: {dc.climate}")
        print_message(f"\n  Starting Capital: ${self.state.money:,.0f}", style="bold yellow")
        
        input("\nPress Enter to begin...")
    
    def handle_main_menu(self, choice):
        """Handle main menu selection"""
        if choice == "s":
            show_statistics(self.state)
        elif choice == "u":
            self.handle_upgrades()
        elif choice == "m":
            self.handle_clients()
        elif choice == "r":
            self.handle_incidents()
        elif choice == "a":
            self.advance_day()
        elif choice == "q":
            self.quit_game()
        else:
            print_message("Invalid choice", style="red")
            input("Press enter to continue...")
    
    def handle_upgrades(self):
        """Handle infrastructure upgrades"""
        while True:
            choice = show_upgrade_menu(self.state)
            
            if choice == "1":
                if self.state.money >= 50000:
                    self.state.servers.append(
                        Hardware(f"srv_{len(self.state.servers)}", 
                                f"Server {len(self.state.servers)}", 
                                health=100, power_draw=500)
                    )
                    self.state.money -= 50000
                    print_message("✓ Server added!", style="bold green")
                    input("Press enter...")
                else:
                    print_message("✗ Insufficient funds", style="red")
                    input("Press enter...")
            
            elif choice == "2":
                if self.state.money >= 40000:
                    self.state.cooling_units.append(
                        Hardware(f"cool_{len(self.state.cooling_units)}", 
                                f"Cooling Unit {len(self.state.cooling_units)}", 
                                health=100, power_draw=200)
                    )
                    self.state.money -= 40000
                    print_message("✓ Cooling unit added!", style="bold green")
                    input("Press enter...")
                else:
                    print_message("✗ Insufficient funds", style="red")
                    input("Press enter...")
            
            elif choice == "3":
                broken_hw = [hw for hw in self.state.servers + self.state.cooling_units 
                            + self.state.power_units + self.state.switches 
                            if hw.health < 100]
                
                if broken_hw:
                    cost = len(broken_hw) * 15000
                    if self.state.money >= cost:
                        for hw in broken_hw:
                            hw.health = 100
                        self.state.money -= cost
                        print_message(f"✓ Repaired {len(broken_hw)} components!", style="bold green")
                        input("Press enter...")
                    else:
                        print_message("✗ Insufficient funds", style="red")
                        input("Press enter...")
                else:
                    print_message("✓ All hardware at full health", style="bold green")
                    input("Press enter...")
            
            elif choice == "4":
                if self.state.money >= 75000:
                    self.state.money -= 75000
                    # Improve UPS
                    for ups in self.state.power_units:
                        ups.power_draw = 0  # UPS doesn't draw power
                    print_message("✓ UPS upgraded!", style="bold green")
                    input("Press enter...")
                else:
                    print_message("✗ Insufficient funds", style="red")
                    input("Press enter...")
            
            elif choice == "b":
                break
    
    def handle_clients(self):
        """Handle client management"""
        while True:
            choice = show_clients_menu(self.state)
            
            if choice == "a":
                if self.state.money >= 20000:
                    self.state.hosted_clients += 1
                    self.state.money -= 20000
                    print_message("✓ 1 new client acquired!", style="bold green")
                    input("Press enter...")
                else:
                    print_message("✗ Insufficient funds", style="red")
                    input("Press enter...")
            
            elif choice == "p":
                if self.state.money >= 100000:
                    self.state.hosted_clients += 3
                    self.state.money -= 100000
                    self.state.reputation = max(0, self.state.reputation - 10)
                    print_message("✓ Poached 3 clients! (Reputation -10)", style="bold yellow")
                    input("Press enter...")
                else:
                    print_message("✗ Insufficient funds", style="red")
                    input("Press enter...")
            
            elif choice == "b":
                break
    
    def handle_incidents(self):
        """Handle incident response"""
        if not self.state.active_incidents:
            show_incidents_menu(self.state)
            return
        
        choice = show_incidents_menu(self.state)
        
        if choice == "1":
            if self.state.money >= 5000:
                self.state.money -= 5000
                if random.random() < 0.7:
                    self.state.active_incidents.pop(0)
                    print_message("✓ Incident resolved!", style="bold green")
                else:
                    print_message("✗ Quick fix failed, incident worsened", style="red")
                    # Damage some hardware
                    if self.state.servers:
                        self.state.servers[0].health -= 20
                input("Press enter...")
            else:
                print_message("✗ Insufficient funds", style="red")
                input("Press enter...")
        
        elif choice == "2":
            if self.state.money >= 15000:
                self.state.money -= 15000
                if random.random() < 0.95:
                    if self.state.active_incidents:
                        self.state.active_incidents.pop(0)
                    print_message("✓ Professional repair successful!", style="bold green")
                else:
                    print_message("✗ Repair attempt failed", style="red")
                input("Press enter...")
            else:
                print_message("✗ Insufficient funds", style="red")
                input("Press enter...")
        
        elif choice == "3":
            print_message("Ignoring incident... This could escalate!", style="yellow")
            self.state.reputation -= 5
            input("Press enter...")
    
    def advance_day(self):
        """Simulate one day and check game over conditions"""
        self.state.simulate_day()
        
        # Game over conditions
        if self.state.money <= 0:
            clear_screen()
            print_banner()
            print_message("\n[bold red]BANKRUPTCY![/bold red]", style="bold red")
            print_message(f"You ran out of money on day {self.state.day}")
            print_message(f"Final Reputation: {self.state.reputation:.1f}")
            self.running = False
        
        elif self.state.get_total_health() < 10:
            clear_screen()
            print_banner()
            print_message("\n[bold red]SYSTEM FAILURE![/bold red]", style="bold red")
            print_message(f"Your infrastructure failed catastrophically on day {self.state.day}")
            print_message("All clients lost!")
            self.running = False
        
        else:
            print_message(f"\n[bold cyan]Day {self.state.day}[/bold cyan] - Systems operational", style="bold green")
            print_message(f"Net income today: ${self.state.monthly_revenue:,.0f}", style="yellow")
            input("Press enter to continue...")
    
    def quit_game(self):
        """Quit the game"""
        print_message("\nThanks for playing Data Center Death!", style="bold cyan")
        print_message(f"Final Score - Day {self.state.day}, Reputation: {self.state.reputation:.1f}, Money: ${self.state.money:,.0f}")
        self.running = False
    
    def run(self):
        """Main game loop"""
        self.initialize_game()
        
        while self.running:
            choice = show_main_menu(self.state)
            self.handle_main_menu(choice)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

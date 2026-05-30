from dataclasses import dataclass, field
from typing import Dict, List
import random
from datetime import datetime

@dataclass
class Hardware:
    """Represents a piece of hardware in the data center"""
    id: str
    name: str
    health: float = 100.0  # 0-100
    power_draw: float = 0.0  # watts
    
    def degrade(self):
        """Hardware degrades over time"""
        self.health = max(0, self.health - random.uniform(0.5, 2.0))
    
    def is_failed(self) -> bool:
        return self.health <= 0

@dataclass
class DataCenter:
    """Represents a data center location"""
    name: str
    location: str
    power_capacity: float  # MW
    cooling_capacity: float  # tons/hour
    base_cost: float  # monthly operational cost
    climate: str  # hot, cold, temperate
    
    def __init__(self, name: str, location: str, power: float, cooling: float, cost: float, climate: str):
        self.name = name
        self.location = location
        self.power_capacity = power
        self.cooling_capacity = cooling
        self.base_cost = cost
        self.climate = climate

# Predefined data center locations
DATA_CENTER_LOCATIONS = {
    "oregon": DataCenter(
        "Portland Data Center", "Portland, Oregon", 
        power=50, cooling=300, cost=150000, climate="cold"
    ),
    "iowa": DataCenter(
        "Des Moines Hub", "Des Moines, Iowa",
        power=45, cooling=250, cost=120000, climate="temperate"
    ),
    "arizona": DataCenter(
        "Phoenix Operations", "Phoenix, Arizona",
        power=55, cooling=400, cost=140000, climate="hot"
    ),
    "virginia": DataCenter(
        "Ashburn Facility", "Ashburn, Virginia",
        power=60, cooling=320, cost=180000, climate="temperate"
    ),
    "iceland": DataCenter(
        "Reykjavik Green", "Reykjavik, Iceland",
        power=40, cooling=200, cost=160000, climate="cold"
    ),
}

@dataclass
class GameState:
    """Main game state"""
    current_datacenter: str = ""
    day: int = 1
    money: float = 1000000.0  # Starting capital
    reputation: float = 50.0  # 0-100
    
    # Infrastructure
    servers: List[Hardware] = field(default_factory=list)
    cooling_units: List[Hardware] = field(default_factory=list)
    power_units: List[Hardware] = field(default_factory=list)
    switches: List[Hardware] = field(default_factory=list)
    
    # Operational
    hosted_clients: int = 0
    monthly_revenue: float = 0.0
    current_load: float = 0.0  # percentage of capacity
    
    # Alerts/Events
    active_incidents: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.servers:
            # Initialize with some basic hardware
            self.servers = [
                Hardware(f"srv_{i}", f"Server {i}", health=100, power_draw=500)
                for i in range(5)
            ]
            self.cooling_units = [
                Hardware("cool_1", "Main Cooler", health=100, power_draw=200)
            ]
            self.power_units = [
                Hardware("ups_1", "UPS Battery", health=100, power_draw=0)
            ]
            self.switches = [
                Hardware("sw_1", "Core Switch", health=100, power_draw=50)
            ]
    
    def get_total_health(self) -> float:
        """Average health of all critical systems"""
        all_hw = self.servers + self.cooling_units + self.power_units + self.switches
        if not all_hw:
            return 100.0
        return sum(hw.health for hw in all_hw) / len(all_hw)
    
    def get_power_draw(self) -> float:
        """Total current power draw in watts, convert to MW"""
        total = sum(hw.power_draw for hw in self.servers + self.cooling_units + self.power_units + self.switches)
        return total / 1_000_000  # Convert watts to MW
    
    def simulate_day(self):
        """Simulate one day of operations"""
        self.day += 1
        
        # Degrade all hardware
        for hw in self.servers + self.cooling_units + self.power_units + self.switches:
            hw.degrade()
        
        # Random incidents (1-3% chance per day)
        if random.random() < 0.02:
            self._trigger_incident()
        
        # Process revenue
        self.monthly_revenue = self.hosted_clients * 5000  # per client per day
        self.money += self.monthly_revenue
        
        # Process operational costs
        power_cost = self.get_power_draw() * 100  # $/MW
        cooling_cost = len(self.cooling_units) * 5000
        maintenance_cost = len(self.servers) * 1000
        
        dc = DATA_CENTER_LOCATIONS.get(self.current_datacenter)
        if dc:
            base_cost = dc.base_cost / 30  # daily portion
            self.money -= (base_cost + power_cost + cooling_cost + maintenance_cost)
        
        # Update reputation based on uptime
        if self.get_total_health() < 50:
            self.reputation -= 5
        elif self.get_total_health() > 80:
            self.reputation += 1
        
        self.reputation = max(0, min(100, self.reputation))
    
    def _trigger_incident(self):
        """Generate a random incident"""
        incidents = [
            "Power surge detected in sector 3",
            "Cooling unit showing elevated temps",
            "Disk failure on Server 2",
            "Network latency spike detected",
            "UPS battery degradation alert",
        ]
        incident = random.choice(incidents)
        self.active_incidents.append(incident)
        if len(self.active_incidents) > 5:
            self.active_incidents.pop(0)

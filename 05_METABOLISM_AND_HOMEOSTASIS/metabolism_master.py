import math

class A7DO_Metabolism:
    """
    MASTER METABOLISM SYSTEM FOR FOLDER 05
    Manages Energy, Thermal Regulation, Hydration, and Homeostatic Drives.
    """

    def __init__(self, core_ref):
        self.core = core_ref
        
        # 1. CORE RESOURCES
        self.energy_reserves = 100.0  # 0.0 to 100.0
        self.hydration_level = 100.0
        self.body_temperature = 37.0  # Celsius standard
        
        # 2. METABOLIC RATES (Changes with development)
        self.basal_metabolic_rate = 0.01 
        self.thermal_efficiency = 0.5 
        
        # 3. HOMEOSTATIC DRIVES (Signals sent to Folder 06: Limbic)
        self.hunger_drive = 0.0
        self.thirst_drive = 0.0
        self.sleep_debt = 0.0

    def update_metabolic_state(self, world_temp):
        """
        Updates internal vitals based on World physics and internal activity.
        """
        stage = self.core.current_stage
        
        # --- DEVELOPMENTAL LOGIC ---
        if stage == "Gestation":
            # Passive Homeostasis: Provided by the 'Environment'
            self.energy_reserves = 100.0
            self.hydration_level = 100.0
            self.body_temperature = 37.0 # Perfectly regulated
            self.basal_metabolic_rate = 0.005
            
        elif stage in ["Neonate", "Infancy", "Adult"]:
            # Active Homeostasis: A7DO must now 'burn' energy to live
            self._process_active_burn()
            self._regulate_temperature(world_temp)
            self._calculate_drives()

        # Update sleep debt based on Core activity
        if self.core.is_sleeping:
            self.sleep_debt = max(0, self.sleep_debt - 0.2)
            self.energy_reserves = min(100.0, self.energy_reserves + 0.05)
        else:
            self.sleep_debt += 0.02

    def _process_active_burn(self):
        """Burn energy based on movement and neural load."""
        # Baseline drain
        drain = self.basal_metabolic_rate
        
        # Higher drain if A7DO is 'thinking' or 'moving'
        # (This will eventually hook into Folders 02 and 03)
        self.energy_reserves -= drain
        self.hydration_level -= (drain * 1.5)
        
        # Bounds check
        self.energy_reserves = max(0, self.energy_reserves)
        self.hydration_level = max(0, self.hydration_level)

    def _regulate_temperature(self, external_temp):
        """Thermoregulation: Trying to maintain 37°C."""
        diff = external_temp - self.body_temperature
        
        # Body slowly drifts toward ambient temp unless metabolic effort is made
        adjustment = diff * (1.0 - self.thermal_efficiency) * 0.01
        self.body_temperature += adjustment
        
        # Metabolic cost of shivering/sweating
        if abs(diff) > 5:
            self.energy_reserves -= 0.02 # Cost of regulation

    def _calculate_drives(self):
        """Translates low resources into 'Drives' for the Limbic system."""
        self.hunger_drive = 1.0 - (self.energy_reserves / 100.0)
        self.thirst_drive = 1.0 - (self.hydration_level / 100.0)

    def ingest_resource(self, resource_type, amount):
        """Allows NPCs or A7DO to restore resources post-birth."""
        if resource_type == "nutrients":
            self.energy_reserves = min(100.0, self.energy_reserves + amount)
        elif resource_type == "hydration":
            self.hydration_level = min(100.0, self.hydration_level + amount)

    def get_metabolic_report(self):
        """Summary for Folder 12 Dashboard."""
        return {
            "energy": f"{self.energy_reserves:.1f}%",
            "hydration": f"{self.hydration_level:.1f}%",
            "temp": f"{self.body_temperature:.1f}°C",
            "status": "Optimal" if self.energy_reserves > 50 else "Seeking Resources",
            "sleep_need": "High" if self.sleep_debt > 5.0 else "Low"
        }

# --- Standalone Test ---
if __name__ == "__main__":
    class MockCore:
        def __init__(self):
            self.current_stage = "Infancy"
            self.is_sleeping = False
            
    core = MockCore()
    metabolism = A7DO_Metabolism(core)
    
    print("--- A7DO Metabolism & Homeostasis ---")
    # Simulate a few cycles in a cold world (10°C)
    for _ in range(10):
        metabolism.update_metabolic_state(world_temp=10.0)
    
    status = metabolism.get_metabolic_report()
    print(f"Post-exposure Vitals: {status}")
    print(f"Hunger Drive: {metabolism.hunger_drive:.2f}")


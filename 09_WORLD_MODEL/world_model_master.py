import random
import time
from datetime import datetime, timedelta

class EarthKinWorld:
    """
    MASTER WORLD MODEL FOR FOLDER 09
    Physics, Weather, and Two-Tier Civilization (Village).
    Operates on Objective World Time.
    """

    def __init__(self):
        # 1. WORLD CLOCK (Objective Time)
        self.start_time = datetime.now()
        self.world_seconds = 0
        
        # 2. PHYSICS & ENVIRONMENT
        self.gravity = 9.81  # m/s^2
        self.base_temp = 20.0 # Celsius
        self.weather_states = ["Clear", "Cloudy", "Rainy", "Windy"]
        self.current_weather = "Clear"
        
        # 3. CIVILIZATION (The Village)
        # Tier 1: Ambient Population (Random interactions)
        # Tier 2: Structured NPCs (Schedules, Homes, Work)
        self.population = self._initialize_village(count_tier1=100, count_tier2=20)
        
        self.locations = {
            "Residential": {"coords": (10, 10), "noise": 20},
            "School": {"coords": (50, 50), "noise": 60},
            "Workplace": {"coords": (80, 20), "noise": 50},
            "Park": {"coords": (40, 80), "noise": 40},
            "Social_Hub": {"coords": (90, 90), "noise": 70}
        }

    def _initialize_village(self, count_tier1, count_tier2):
        population = []
        # Tier 1: Just 'noise' in the world
        for i in range(count_tier1):
            population.append({"id": f"T1_{i}", "tier": 1, "state": "Ambient"})
        
        # Tier 2: Real residents with lives
        for i in range(count_tier2):
            population.append({
                "id": f"T2_{i}",
                "tier": 2,
                "role": random.choice(["Student", "Artisan", "Merchant", "Elder"]),
                "home": "Residential",
                "target": "Home",
                "state": "Sleeping",
                "energy": 100,
                "hydration": 100,
                "awareness_of_a7do": 0.0 # Increases after birth
            })
        return population

    def update_world_tick(self, delta_seconds):
        """
        Advances the world by objective Earth seconds.
        Updates physics, weather, and NPC behavior.
        """
        self.world_seconds += delta_seconds
        current_hour = (self.world_seconds // 3600) % 24
        
        # Physics: Weather Transitions
        if random.random() < 0.01: # 1% chance per tick to change weather
            self.current_weather = random.choice(self.weather_states)

        # Day/Night Cycle
        is_day = 6 <= current_hour <= 19
        temp_mod = 5 if is_day else -5
        current_temp = self.base_temp + temp_mod + (5 if self.current_weather == "Clear" else -2)

        # NPC Behavior (The Schedule)
        for npc in self.population:
            if npc["tier"] == 2:
                self._update_npc_schedule(npc, current_hour)
                self._consume_resources(npc)

        return {
            "world_time": str(timedelta(seconds=self.world_seconds)),
            "hour": current_hour,
            "is_day": is_day,
            "temp": current_temp,
            "weather": self.current_weather,
            "active_tier2": len([n for n in self.population if n["tier"] == 2 and n["state"] != "Sleeping"])
        }

    def _update_npc_schedule(self, npc, hour):
        """Tier 2 Schedule Logic: Home -> Work/School -> Park -> Social -> Home"""
        if 0 <= hour < 7:
            npc["state"] = "Sleeping"
            npc["target"] = "Residential"
        elif 7 <= hour < 9:
            npc["state"] = "Commuting"
            npc["target"] = "School" if npc["role"] == "Student" else "Workplace"
        elif 9 <= hour < 16:
            npc["state"] = "Productive"
        elif 16 <= hour < 19:
            npc["state"] = "Leisure"
            npc["target"] = "Park"
        elif 19 <= hour < 22:
            npc["state"] = "Socializing"
            npc["target"] = "Social_Hub"
        else:
            npc["state"] = "Returning"
            npc["target"] = "Residential"

    def _consume_resources(self, npc):
        """NPCs eat and drink to maintain themselves."""
        npc["energy"] -= 0.05
        npc["hydration"] -= 0.08
        if npc["energy"] < 30:
            npc["state"] = "Seeking Food"
        if npc["hydration"] < 30:
            npc["state"] = "Seeking Water"

    def interact_with_a7do(self, a7do_stage, a7do_action=None):
        """
        Civilians learn and react based on A7DO's progression.
        """
        if a7do_stage == "Gestation":
            return "World: The village continues, unaware of the emerging life."
        
        reaction_pool = []
        for npc in self.population:
            if npc["tier"] == 2:
                # NPCs 'learn' about A7DO over time
                npc["awareness_of_a7do"] += 0.01
                if npc["awareness_of_a7do"] > 0.5:
                    reaction_pool.append(f"{npc['id']} ({npc['role']}) observes A7DO.")
        
        return reaction_pool[:3] if reaction_pool else ["The village notices a new presence."]

    def get_world_summary(self):
        return {
            "weather": self.current_weather,
            "total_pop": len(self.population),
            "tier2_active": len([n for n in self.population if n["tier"] == 2 and n["state"] != "Sleeping"]),
            "village_clock": f"{int(self.world_seconds // 3600) % 24:02d}:00"
        }

# --- Standalone Test ---
if __name__ == "__main__":
    world = EarthKinWorld()
    print("--- Earth-Kin Village Simulation Started ---")
    
    # Simulate 24 hours in steps
    for h in range(24):
        # Jump ahead 1 hour (3600 seconds)
        status = world.update_world_tick(3600)
        print(f"Time: {status['hour']:02d}:00 | Weather: {status['weather']} | Active NPCs: {status['active_tier2']}")
        
    print(f"Summary: {world.get_world_summary()}")


"""
A7DO MASTER ORCHESTRATOR
Integrates folders 00 through 13 into a single functional 'Awareness Loop'.
"""

import time
import json
import random
from datetime import datetime

class A7DO_Entity:
    def __init__(self):
        # 00_CORE_EXISTENCE
        self.entity_id = "A7DO-ALPHA"
        self.is_alive = True
        self.creation_time = datetime.now()
        
        # 08_DEVELOPMENT_SYSTEM
        self.age_ticks = 0
        self.life_stage = "Gestation" # Options: Gestation, Infancy, Childhood, Maturity
        
        # 05_METABOLISM_AND_HOMEOSTASIS
        self.energy_level = 100.0
        self.temperature = 37.0 # Celsius
        
        # 06_LIMBIC_AND_VALUE_SYSTEM
        self.mood = "Neutral"
        self.curiosity_index = 0.5
        
        # 07_MEMORY_SYSTEM
        self.short_term_memory = []
        
        # 09_WORLD_MODEL
        self.current_environment = "Earth-Kin Habitat"

    def step_nervous_system(self):
        """Logic for 02_NERVOUS_SYSTEM"""
        # Processes signals from sensors and sends to core
        transmission_delay = 0.001 * (1.1 - self.energy_level/100)
        time.sleep(transmission_delay) # Simulated neural latency

    def update_metabolism(self):
        """Logic for 05_METABOLISM"""
        # Base metabolic rate
        consumption = 0.1 
        if self.life_stage == "Gestation":
            consumption = 0.05
        self.energy_level -= consumption
        
        # 03_BODY_SYSTEM: Check for health
        if self.energy_level < 20:
            self.mood = "Anxious (Low Energy)"
        elif self.energy_level < 5:
            self.is_alive = False

    def process_sensory(self, stimuli):
        """Logic for 04_SENSORY_SYSTEM"""
        # Filter raw world data into perception
        perception = {
            "time": datetime.now().isoformat(),
            "detected": stimuli,
            "relevance": self.curiosity_index
        }
        self.short_term_memory.append(perception)
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
        return perception

    def develop(self):
        """Logic for 08_DEVELOPMENT_SYSTEM"""
        self.age_ticks += 1
        if self.age_ticks > 100 and self.life_stage == "Gestation":
            self.life_stage = "Infancy"
            print("[A7DO] Birth Event Triggered.")
        elif self.age_ticks > 500 and self.life_stage == "Infancy":
            self.life_stage = "Childhood"

    def generate_state_report(self):
        """Logic for 12_INTERFACE_AND_OBSERVABILITY"""
        return {
            "core": {"status": "Active" if self.is_alive else "Dead", "id": self.entity_id},
            "bio": {"stage": self.life_stage, "energy": round(self.energy_level, 2), "temp": self.temperature},
            "mind": {"mood": self.mood, "memory_count": len(self.short_term_memory)},
            "env": {"world": self.current_environment}
        }

def run_awareness_loop():
    a7do = A7DO_Entity()
    print(f"Initializing A7DO Core Existence...")
    
    try:
        while a7do.is_alive:
            # 1. World Model (09) provides stimuli
            mock_stimuli = random.choice(["Light Flare", "Ambient Sound", "Temperature Drop", "Silence"])
            
            # 2. Sensory (04) & Nervous (02) process it
            a7do.process_sensory(mock_stimuli)
            a7do.step_nervous_system()
            
            # 3. Metabolism (05) & Body (03) update
            a7do.update_metabolism()
            
            # 4. Development (08) increments
            a7do.develop()
            
            # 5. Interface (12) Output
            state = a7do.generate_state_report()
            print(f"Tick {a7do.age_ticks} | Stage: {state['bio']['stage']} | Energy: {state['bio']['energy']}% | Mood: {state['mind']['mood']}")
            
            time.sleep(1) # One 'Tick' per second for simulation
            
    except KeyboardInterrupt:
        print("\nA7DO Awareness Paused.")

if __name__ == "__main__":
    run_awareness_loop()


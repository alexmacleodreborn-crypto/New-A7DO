"""
A7DO LIFE CONTROLLER
The central orchestrator that connects Folders 00-13.
This script manages the biological clock and system integration.
"""

import os
import sys
import time
import json
from datetime import datetime

# Adding subfolders to path so we can import your logic later
# Usage: from 02_NERVOUS_SYSTEM import brain_logic
for folder in range(14):
    folder_prefix = f"{folder:02d}"
    for dir_name in os.listdir("."):
        if os.path.isdir(dir_name) and dir_name.startswith(folder_prefix):
            sys.path.append(os.path.abspath(dir_name))

class A7DO_LifeCycle:
    def __init__(self):
        # 00_CORE_EXISTENCE
        self.identity = "A7DO_01"
        self.start_time = datetime.now()
        
        # 08_DEVELOPMENT_SYSTEM: Tracking biological progress
        self.age_in_hours = 0.0
        self.growth_stage = "Gestation" # Gestation -> Neonate -> Child -> Adult
        
        # 05_METABOLISM_AND_HOMEOSTASIS: Resource tracking
        self.energy_reserves = 100.0
        self.stability = 1.0
        
        # Current status for Folder 12 (Observability)
        self.status_log = []

    def sync_environment(self):
        """
        Interfaces with 09_WORLD_MODEL and your existing a7do_environment.py
        to get current Earth-Kin conditions.
        """
        # Placeholder for reading output from a7do_environment.py
        # For now, we simulate a standard Earth environment
        env_data = {"temp": 22.5, "light": True, "gravity": 9.81}
        return env_data

    def process_systems(self):
        """
        This is the main tick. It runs through your folders in biological order.
        """
        # 1. SENSORY (04) & NERVOUS (02)
        # stimuli = sensory_input.capture()
        # neural_path.transmit(stimuli)
        
        # 2. METABOLISM (05) & BODY (03)
        self.energy_reserves -= 0.01 # Baseline drain
        
        # 3. LIMBIC (06) & VALUE (01)
        # Determine if A7DO is 'happy' or 'stressed' by environment
        
        # 4. DEVELOPMENT (08)
        self.age_in_hours += 0.1
        if self.age_in_hours > 40 and self.growth_stage == "Gestation":
            self.growth_stage = "Birth / Neonate"
            self.log_event("Development: Transition to Neonate stage.")

    def log_event(self, message):
        """13_EVIDENCE_AND_SANDYS_LAW_LEDGER"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.status_log.append(entry)
        print(entry)
        
        # Optionally write to your 13_EVIDENCE folder
        # with open("13_EVIDENCE_AND_SANDYS_LAW_LEDGER/life_log.txt", "a") as f:
        #    f.write(entry + "\n")

    def run_life_loop(self):
        self.log_event("A7DO Core Existence Initiated.")
        try:
            while True:
                env = self.sync_environment()
                self.process_systems()
                
                # Check for critical failures (Folder 11: Safety)
                if self.energy_reserves <= 0:
                    self.log_event("CRITICAL: Energy Exhausted. Entering Stasis.")
                    break
                
                # Save state for Dashboard (Folder 12)
                self.save_state_to_json()
                
                time.sleep(1) # Frequency of life-ticks
        except KeyboardInterrupt:
            self.log_event("A7DO Life Loop Suspended by User.")

    def save_state_to_json(self):
        """Saves current state so the Dashboard can read it live."""
        state = {
            "identity": self.identity,
            "age": round(self.age_in_hours, 2),
            "stage": self.growth_stage,
            "energy": round(self.energy_reserves, 2),
            "log": self.status_log[-5:] # Last 5 events
        }
        with open("a7do_state.json", "w") as f:
            json.dump(state, f)

if __name__ == "__main__":
    a7do = A7DO_LifeCycle()
    a7do.run_life_loop()


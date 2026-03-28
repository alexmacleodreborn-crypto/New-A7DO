import random

class A7DO_Limbic:
    """
    MASTER LIMBIC & VALUE SYSTEM FOR FOLDER 06
    Handles Emotions, Valuation, Drives, and Behavioral Choices.
    This is the seat of A7DO's 'Free Will' and 'Personality'.
    """

    def __init__(self, core_ref, metabolism_ref):
        self.core = core_ref
        self.metabolism = metabolism_ref
        
        # 1. EMOTIONAL STATE (Folder 06/emotions)
        # Using a multi-dimensional emotional model
        self.emotions = {
            "joy": 0.5,        # 0.0 to 1.0
            "distress": 0.0,
            "fear": 0.0,
            "curiosity": 0.5,
            "calm": 1.0
        }
        
        # 2. VALUE SYSTEM (Folder 06/values)
        # What A7DO 'likes' or 'dislikes' (learned over time)
        self.value_ledger = {
            "warmth": 1.0,     # Essential for survival
            "light": 0.2,      # Neutral/Positive
            "interaction": 0.0 # Starts at zero in gestation
        }

        # 3. CURRENT INTENT
        self.dominant_drive = "Stability"
        self.active_choice = "Existing"

    def update_emotional_loop(self, sensory_perception):
        """
        The emotional core reacts to internal drives and external stimuli.
        """
        stage = self.core.current_stage
        
        # --- INFLUENCE 1: METABOLIC DRIVES ---
        # High hunger or thirst increases distress and fear (survival instinct)
        hunger = self.metabolism.hunger_drive
        thirst = self.metabolism.thirst_drive
        
        if hunger > 0.5 or thirst > 0.5:
            self.emotions["distress"] = min(1.0, self.emotions["distress"] + 0.1)
            self.emotions["joy"] = max(0.0, self.emotions["joy"] - 0.05)
            self.emotions["calm"] = max(0.0, self.emotions["calm"] - 0.1)

        # --- INFLUENCE 2: SENSORY PERCEPTION ---
        # A7DO reacts to symbols perceived in the village
        if "visual_symbol" in sensory_perception:
            symbol = sensory_perception["visual_symbol"]
            if symbol == "Existence: Illumination":
                self.emotions["joy"] = min(1.0, self.emotions["joy"] + 0.02)
                self.emotions["curiosity"] += 0.01

        if sensory_perception.get("thermal_state") == "Distress":
            self.emotions["fear"] = min(1.0, self.emotions["fear"] + 0.05)

        # --- STAGE-BASED LIMITATIONS ---
        if stage == "Gestation":
            # Very limited emotional range; mostly 'Calm' or 'Primal Distress'
            self.emotions["joy"] = 0.5
            self.emotions["curiosity"] = 0.1
            self.emotions["distress"] *= 0.1 # Numbed by biology

        self._normalize_emotions()

    def make_behavioral_choice(self):
        """
        Determines A7DO's current priority based on its 'Freedom'.
        A7DO is free to ignore a drive if curiosity or fear is higher.
        """
        stage = self.core.current_stage
        
        if stage == "Gestation":
            self.active_choice = "Biological Growth"
            return self.active_choice

        # The 'Freedom' calculation: A7DO weighs emotions vs drives
        choices = ["Explore", "Seek Comfort", "Rest", "Interact"]
        
        # Determine weightings
        weights = [
            self.emotions["curiosity"],    # Explore
            self.emotions["distress"],     # Seek Comfort
            self.metabolism.sleep_debt,    # Rest
            self.emotions["joy"]           # Interact
        ]
        
        # Pick the highest weighted action, but add a bit of randomness (Freedom)
        if random.random() < 0.1: # 10% chance to do something random/free
            self.active_choice = random.choice(choices)
        else:
            max_val = max(weights)
            idx = weights.index(max_val)
            self.active_choice = choices[idx]
            
        return self.active_choice

    def _normalize_emotions(self):
        """Ensures emotional values stay within bounds and decay naturally."""
        for emotion in self.emotions:
            # Natural decay toward baseline (homeostasis of the mind)
            if emotion != "calm":
                self.emotions[emotion] = max(0.0, self.emotions[emotion] - 0.001)
            else:
                self.emotions["calm"] = min(1.0, self.emotions["calm"] + 0.001)
            
            # Clamp values
            self.emotions[emotion] = round(min(max(self.emotions[emotion], 0.0), 1.0), 3)

    def get_limbic_report(self):
        """Summary for Folder 12 Dashboard."""
        return {
            "mood": "Stable" if self.emotions["distress"] < 0.3 else "Distressed",
            "joy_index": f"{self.emotions['joy'] * 100:.1f}%",
            "fear_index": f"{self.emotions['fear'] * 100:.1f}%",
            "current_choice": self.active_choice,
            "freedom_level": "Biological/Restricted" if self.core.current_stage == "Gestation" else "High"
        }

# --- Standalone Test ---
if __name__ == "__main__":
    class MockCore:
        def __init__(self):
            self.current_stage = "Infancy"
            self.is_sleeping = False
            
    class MockMetabolism:
        def __init__(self):
            self.hunger_drive = 0.8 # Very hungry
            self.sleep_debt = 0.1
            
    core = MockCore()
    meta = MockMetabolism()
    limbic = A7DO_Limbic(core, meta)
    
    print("--- A7DO Limbic & Value System ---")
    
    # Perception of a new light in the village
    sensory = {"visual_symbol": "Existence: Illumination", "thermal_state": "Comfort"}
    
    limbic.update_emotional_loop(sensory)
    choice = limbic.make_behavioral_choice()
    
    status = limbic.get_limbic_report()
    print(f"Emotions: Joy {status['joy_index']} | Fear {status['fear_index']}")
    print(f"A7DO Choice: {choice} (Drive: {status['mood']})")


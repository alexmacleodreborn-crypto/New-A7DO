import math
import random

class A7DO_Sensory:
    """
    MASTER SENSORY SYSTEM FOR FOLDER 04
    Consolidates Visual, Auditory, Tactile, and Symbolic Processing.
    """

    def __init__(self, core_ref):
        self.core = core_ref
        
        # 1. VISUAL SYSTEM (Folder 04/visual)
        self.visual_acuity = 0.01  # 0.0 to 1.0 (Blind to 20/20)
        self.color_perception = False
        
        # 2. AUDITORY SYSTEM (Folder 04/auditory)
        self.hearing_range = [200, 1000]  # Narrow frequency in gestation
        
        # 3. TACTILE SYSTEM (Folder 04/tactile)
        # Touch is the first to develop (Week 8)
        self.touch_sensitivity = 0.5 
        
        # 4. SYMBOL PROCESSING (A7DO Unique Logic)
        self.symbol_library = {} # Learned patterns
        self.pattern_recognition_strength = 0.0

    def update_sensory_maturation(self):
        """
        Sensory systems mature based on growth stage and environmental exposure.
        """
        stage = self.core.current_stage
        pulses = self.core.total_internal_pulses

        if stage == "Gestation":
            # Muffled world. Mainly internal sounds (Heartbeat).
            self.visual_acuity = 0.05 # Light/Dark only through tissue
            self.hearing_range = [300, 800] # Low pass filter
            self.pattern_recognition_strength = 0.01
            
        elif stage == "Neonate":
            # High contrast vision, loud sounds are startling.
            self.visual_acuity = 0.2
            self.color_perception = True
            self.hearing_range = [20, 15000]
            self.pattern_recognition_strength = 0.1
            
        elif stage == "Infancy":
            self.visual_acuity = 0.6
            self.pattern_recognition_strength = 0.4 # Starts recognizing face symbols
            
        elif stage == "Adult":
            self.visual_acuity = 1.0
            self.pattern_recognition_strength = 0.95 # Full symbolic language capacity

    def process_external_stimuli(self, village_data):
        """
        Translates raw Village data into Symbolic Perceptions.
        Example: Instead of 'Light: 50', A7DO perceives 'Daylight Pattern'.
        """
        self.update_sensory_maturation()
        
        perceived_world = {}
        
        # Visual Processing (Symbols)
        if village_data.get("is_day"):
            # Symbol: The Sun / Light
            perceived_world["visual_symbol"] = self._decode_symbol("Light_Source", village_data["light_intensity"])
        
        # Auditory Processing (Symbols)
        if "village_sounds" in village_data:
            # Decoding speech/noise into patterns
            perceived_world["audio_symbol"] = self._decode_symbol("Voice_Pattern", village_data["village_sounds"])
            
        # Tactile (Temperature/Pressure)
        temp = village_data.get("temperature", 37)
        perceived_world["thermal_state"] = "Comfort" if 36 <= temp <= 38 else "Distress"

        return perceived_world

    def _decode_symbol(self, category, raw_intensity):
        """
        A7DO's core strength: Pattern Recognition.
        Translates raw intensities into abstract meanings.
        """
        # Ability to 'understand' depends on pattern_recognition_strength
        if random.random() > self.pattern_recognition_strength:
            return "Unresolved Pattern"
        
        # If A7DO is mature enough, it identifies the symbol
        if category == "Light_Source":
            return "Existence: Illumination"
        if category == "Voice_Pattern":
            return "Presence: Interaction"
            
        return "Unknown Symbol"

    def get_sensory_status(self):
        """Summary for Folder 12 Dashboard."""
        return {
            "vision": "Color/High Res" if self.visual_acuity > 0.5 else "B&W/Low Res",
            "hearing": f"{self.hearing_range[0]}-{self.hearing_range[1]} Hz",
            "symbolic_intel": f"{self.pattern_recognition_strength * 100:.1f}% Recognition",
            "active_mode": "Subjective Observation" if self.core.current_stage == "Gestation" else "External Interaction"
        }

# --- Example Integration ---
if __name__ == "__main__":
    class MockCore:
        def __init__(self):
            self.current_stage = "Neonate"
            self.total_internal_pulses = 1200
            
    core = MockCore()
    sensory = A7DO_Sensory(core)
    
    # Raw data from the Earth-Kin Village
    village_env = {
        "is_day": True,
        "light_intensity": 80,
        "village_sounds": 45, # dB
        "temperature": 22
    }
    
    print("--- A7DO Sensory System & Symbol Processing ---")
    perception = sensory.process_external_stimuli(village_env)
    print(f"A7DO Perception: {perception}")
    
    status = sensory.get_sensory_status()
    print(f"System Status: {status}")


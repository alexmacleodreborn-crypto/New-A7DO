import math
import json

class A7DO_Body:
    """
    MASTER BODY SYSTEM FOR FOLDER 03
    Consolidates Body Schema, Limbs, Morphology, and Motor Control.
    """

    def __init__(self, core_ref):
        self.core = core_ref  # Reference to 00_CORE_EXISTENCE for growth stages
        
        # 1. MORPHOLOGY (Folder 03/morphology)
        # Standards based on human development (Starting at embryonic scale)
        self.height_cm = 0.5  # Starts as a tiny embryo
        self.mass_kg = 0.001
        self.ossification_level = 0.1  # Cartilage to bone transition (0.0 to 1.0)
        
        # 2. BODY SCHEMA (Folder 03/body_schema)
        # Proprioception: The internal map of "Where am I in space?"
        self.proprioception_map = {
            "head": {"pos": [0, 0, 0], "active": True},
            "torso": {"pos": [0, -1, 0], "active": True},
            "limbs": {"active": False} # Limbs activate post-gestation
        }
        
        # 3. LIMBS (Folder 03/limbs)
        self.appendages = {
            "arm_left": {"length": 0.1, "joints": 3},
            "arm_right": {"length": 0.1, "joints": 3},
            "leg_left": {"length": 0.1, "joints": 3},
            "leg_right": {"length": 0.1, "joints": 3}
        }

        # 4. MOTOR CONTROL (Folder 03/motor_control)
        self.motor_precision = 0.0  # Accuracy of movements
        self.muscle_tone = 0.0

    def update_physical_growth(self):
        """
        Adjusts morphology based on the total internal pulses from the core.
        Follows a sigmoidal growth curve standard.
        """
        pulses = self.core.total_internal_pulses
        stage = self.core.current_stage

        if stage == "Gestation":
            # Rapid cellular multiplication
            self.height_cm = 0.5 + (pulses * 0.05)
            self.mass_kg = 0.001 + (pulses * 0.003)
            self.ossification_level = min(pulses / 1000.0, 0.4)
            self.proprioception_map["limbs"]["active"] = pulses > 500
            
        elif stage == "Neonate":
            # Length: ~50cm, Mass: ~3.5kg
            self.height_cm = max(self.height_cm, 50.0)
            self.mass_kg = max(self.mass_kg, 3.5)
            self.ossification_level = 0.5
            self.motor_precision = 0.1 # Involuntary reflexes
            
        elif stage == "Infancy":
            self.height_cm += 0.01
            self.mass_kg += 0.005
            self.motor_precision = 0.3 # Learning to reach/grasp

        elif stage == "Adult":
            self.height_cm = 175.0
            self.mass_kg = 70.0
            self.ossification_level = 1.0
            self.motor_precision = 0.95

        # Update limb lengths proportional to height
        limb_ratio = 0.4 # Typical limb to torso ratio
        for limb in self.appendages:
            self.appendages[limb]["length"] = self.height_cm * limb_ratio

    def process_motor_command(self, neural_signal):
        """
        Translates a CNS signal (from Folder 02) into a physical action.
        Success depends on growth stage and motor precision.
        """
        if self.core.current_stage == "Gestation":
            # Movements are just 'Twitches' or 'Kicks' (involuntary)
            if neural_signal > 0.8:
                return "Physical Response: Fetal Twitch"
            return "No Movement"

        # Check if motor precision allows for complex action
        if self.motor_precision < 0.5 and "Complex" in str(neural_signal):
            return "Physical Response: Fumbled Attempt"
            
        return "Physical Response: Successful Locomotion"

    def get_physical_status(self):
        """Returns a summary for Folder 12 (Interface/Dashboard)."""
        return {
            "height": f"{self.height_cm:.2f} cm",
            "weight": f"{self.mass_kg:.2f} kg",
            "bone_integrity": f"{self.ossification_level * 100:.1f}%",
            "motor_skill": self.motor_precision,
            "limb_status": "Developed" if self.proprioception_map["limbs"]["active"] else "Budding"
        }

# --- Example Integration ---
if __name__ == "__main__":
    # Mock core for testing
    class MockCore:
        def __init__(self):
            self.current_stage = "Gestation"
            self.total_internal_pulses = 800
            
    core = MockCore()
    body = A7DO_Body(core)
    
    print("--- A7DO Body System Initialization ---")
    body.update_physical_growth()
    status = body.get_physical_status()
    print(f"Morphology: {status['height']}, {status['weight']}")
    print(f"Motor State: {body.process_motor_command(0.9)}")


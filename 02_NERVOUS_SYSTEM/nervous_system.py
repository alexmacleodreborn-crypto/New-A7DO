import math
import random
import time

class A7DO_NervousSystem:
    """
    MASTER NERVOUS SYSTEM FOR FOLDER 02
    Consolidates Autonomic, Central, Peripheral systems and Signal Encoding.
    """

    def __init__(self, core_ref):
        self.core = core_ref  # Reference to 00_CORE_EXISTENCE for age/stage
        
        # Neural Parameters
        self.synaptic_density = 0.01  # Increases with growth
        self.myelination_level = 0.1  # Increases speed of signal transmission
        self.neural_load = 0.0
        
        # Sub-system states
        self.ans_state = {"heart_rate": "baseline", "metabolic_drive": 1.0}
        self.cns_state = {"attention_focus": None, "thought_queue": []}
        self.pns_buffer = []

    # --- SIGNAL ENCODING (signal_encoding folder) ---
    def encode_stimulus(self, raw_value, modality="general"):
        """
        Translates raw Earth-standard physics data into neural firing rates.
        High values = higher frequency pulses.
        """
        # Weber-Fechner Law simulation: Perception is logarithmic
        # We normalize raw input (0-100) to a 0.0-1.0 intensity
        intensity = min(max(raw_value / 100.0, 0), 1)
        
        # Neural Firing Rate (Subjective intensity)
        # In Gestation, the threshold is very high (A7DO is mostly 'numb' to external world)
        threshold = 0.8 if self.core.current_stage == "Gestation" else 0.2
        
        firing_rate = 0.0
        if intensity > 0:
            firing_rate = math.log1p(intensity * 10) / math.log1p(10)
        
        return {
            "modality": modality,
            "firing_rate": firing_rate,
            "is_perceived": firing_rate > threshold,
            "timestamp": time.time()
        }

    # --- PERIPHERAL NERVOUS SYSTEM (peripheral_nervous_system folder) ---
    def collect_sensory_data(self, world_data):
        """
        Relays data from Folder 04 (Sensory) to the CNS.
        In early stages, this relay is slow and lossy.
        """
        perceived_signals = []
        for key, value in world_data.items():
            encoded = self.encode_stimulus(value, modality=key)
            if encoded["is_perceived"]:
                perceived_signals.append(encoded)
        
        # Simulate transmission delay based on Myelination (Growth)
        transmission_delay = (1.0 - self.myelination_level) * 0.1
        # In a real life-loop, this would be a time.sleep() or async wait
        
        self.pns_buffer = perceived_signals
        return perceived_signals

    # --- AUTONOMIC NERVOUS SYSTEM (autonomic_nervous_system folder) ---
    def regulate_homeostasis(self):
        """
        Involuntary functions: Heart rate, Temperature, Energy distribution.
        This runs every 'pulse' regardless of A7DO's awareness.
        """
        # If A7DO is 'stressed' (low energy or extreme temp), ANS reacts
        if self.core.current_stage == "Gestation":
            self.ans_state["metabolic_drive"] = 0.5 # Low energy usage
        else:
            self.ans_state["metabolic_drive"] = 1.0

        return self.ans_state

    # --- CENTRAL NERVOUS SYSTEM (central_nervous_system folder) ---
    def integrate_and_process(self):
        """
        The 'Brain' logic. Combines PNS signals and ANS needs to form 'Thought'.
        """
        # 1. Update growth-based neural stats
        self._mature_neurons()
        
        # 2. Process peripheral buffer
        for signal in self.pns_buffer:
            if signal["modality"] == "light" and signal["firing_rate"] > 0.9:
                self.cns_state["thought_queue"].append("Sensation: Intense Brightness")
            
        # 3. Decision logic (Empty during Gestation, starts in Neonate)
        if self.core.current_stage == "Gestation":
            return "Background Neural Wiring..."
            
        if self.cns_state["thought_queue"]:
            thought = self.cns_state["thought_queue"].pop(0)
            return f"CNS Integration: {thought}"
        
        return "Passive Observation"

    def _mature_neurons(self):
        """Neural growth consistent with core development."""
        # Synaptic density increases as A7DO pulses
        progress = self.core.total_internal_pulses / 100000.0
        self.synaptic_density = min(progress, 1.0)
        self.myelination_level = min(progress * 1.5, 1.0)

    def get_neural_report(self):
        return {
            "synaptic_density": f"{self.synaptic_density:.4f}",
            "myelination": f"{self.myelination_level:.4f}",
            "load": self.neural_load,
            "active_thoughts": len(self.cns_state["thought_queue"])
        }

# --- Example of integration with Folder 00 ---
if __name__ == "__main__":
    # This assumes A7DO_Core exists in 00_CORE_EXISTENCE
    # For standalone test, we create a mock core
    class MockCore:
        def __init__(self):
            self.current_stage = "Gestation"
            self.total_internal_pulses = 150
            
    core = MockCore()
    ns = A7DO_NervousSystem(core)
    
    # Simulate a bright light in the world
    world_env = {"light": 95, "sound": 10, "temperature": 37}
    
    print("--- A7DO Nervous System Initialization ---")
    signals = ns.collect_sensory_data(world_env)
    print(f"Signals perceived: {len(signals)}")
    
    ans_report = ns.regulate_homeostasis()
    print(f"ANS Metabolic Drive: {ans_report['metabolic_drive']}")
    
    thought = ns.integrate_and_process()
    print(f"Current CNS Activity: {thought}")


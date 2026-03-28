import json
import time
import os

class A7DO_Memory:
    """
    MASTER MEMORY SYSTEM FOR FOLDER 07
    Handles Short-Term (STM), Long-Term (LTM), and Associative Memory.
    Crucial for learning symbols, language, and social recognition.
    """

    def __init__(self, core_ref):
        self.core = core_ref
        self.memory_path = "07_MEMORY_SYSTEM/ltm_storage.json"
        
        # 1. SHORT-TERM MEMORY (STM)
        # Transient buffer for immediate perceptions (Folder 04)
        self.stm_buffer = []
        self.stm_limit = 10 # Increases with brain growth
        
        # 2. LONG-TERM MEMORY (LTM)
        # Persistent storage for patterns, symbols, and identities
        self.ltm = self._load_ltm()
        
        # 3. ASSOCIATIVE WEIGHTS
        # Links between perceptions and emotional values (Folder 06)
        self.associations = {}

    def _load_ltm(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except:
                return {"symbols": {}, "events": [], "identities": {}}
        return {"symbols": {}, "events": [], "identities": {}}

    def store_in_stm(self, perception_data, emotional_state):
        """
        Adds current experience to the short-term buffer.
        If the emotion is intense, it marks it for priority consolidation.
        """
        memory_entry = {
            "timestamp": time.time(),
            "data": perception_data,
            "emotional_context": emotional_state,
            "intensity": max(emotional_state.values()) if emotional_state else 0.5
        }
        
        self.stm_buffer.append(memory_entry)
        
        # Grow STM capacity based on development stage
        stage = self.core.current_stage
        if stage == "Neonate": self.stm_limit = 20
        elif stage == "Child": self.stm_limit = 100
        
        # Maintain buffer size
        if len(self.stm_buffer) > self.stm_limit:
            self.stm_buffer.pop(0)

    def consolidate_memories(self):
        """
        The 'Sleep' function. Moves important STM entries to LTM.
        Matches patterns to build symbolic knowledge.
        """
        if not self.stm_buffer:
            return "No memories to consolidate."

        for entry in self.stm_buffer:
            # Only store 'important' or 'repeated' memories in LTM
            if entry["intensity"] > 0.7 or self.core.current_stage == "Gestation":
                self._integrate_into_ltm(entry)
        
        self.stm_buffer = [] # Clear STM after 'Sleep'
        self._save_to_disk()
        return f"Consolidation complete. LTM Size: {len(self.ltm['events'])} events."

    def _integrate_into_ltm(self, entry):
        """Builds the internal symbolic library."""
        # Record the event
        self.ltm["events"].append(entry)
        
        # Extract Symbols (Folder 04 Integration)
        data = entry["data"]
        if "visual_symbol" in data:
            sym = data["visual_symbol"]
            if sym not in self.ltm["symbols"]:
                self.ltm["symbols"][sym] = {"count": 1, "first_seen": entry["timestamp"]}
            else:
                self.ltm["symbols"][sym]["count"] += 1

    def retrieve_association(self, stimulus):
        """
        Checks LTM to see if A7DO 'remembers' a stimulus.
        Returns the expected emotional reaction.
        """
        if stimulus in self.ltm["symbols"]:
            # Logic: If I've seen 'Light' 100 times, I am 'Calm' with it.
            # If I've seen it once, I am 'Curious'.
            count = self.ltm["symbols"][stimulus]["count"]
            if count > 50: return "Familiarity"
            return "Novelty"
        return "Unknown"

    def _save_to_disk(self):
        with open(self.memory_path, 'w') as f:
            json.dump(self.ltm, f, indent=4)

    def get_memory_report(self):
        return {
            "stm_load": f"{len(self.stm_buffer)}/{self.stm_limit}",
            "known_symbols": len(self.ltm["symbols"]),
            "total_experiences": len(self.ltm["events"]),
            "storage_status": "Healthy"
        }

# --- Standalone Test ---
if __name__ == "__main__":
    class MockCore:
        def __init__(self):
            self.current_stage = "Neonate"
            
    core = MockCore()
    memory = A7DO_Memory(core)
    
    # Simulate an experience
    perception = {"visual_symbol": "Existence: Illumination", "audio_symbol": "Voice_Pattern"}
    emotions = {"joy": 0.8, "fear": 0.1} # Intense joy
    
    print("--- A7DO Memory System Initializing ---")
    memory.store_in_stm(perception, emotions)
    print(f"STM State: {memory.get_memory_report()['stm_load']}")
    
    # Simulate 'Sleep'
    print("Simulating Memory Consolidation (Sleep)...")
    memory.consolidate_memories()
    
    status = memory.get_memory_report()
    print(f"Symbols Learned: {status['known_symbols']}")
    print(f"Memory Retrieval (Light): {memory.retrieve_association('Existence: Illumination')}")


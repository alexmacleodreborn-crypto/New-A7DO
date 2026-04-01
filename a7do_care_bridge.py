from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A7DO_NervousSystem = load_module(
    "bridge_nervous",
    "02_NERVOUS_SYSTEM/nervous_system.py",
).A7DO_NervousSystem
A7DO_Body = load_module(
    "bridge_body",
    "03_BODY_SYSTEM/body.py",
).A7DO_Body
A7DO_Sensory = load_module(
    "bridge_sensory",
    "04_SENSORY_SYSTEM/a7do_sensory.py",
).A7DO_Sensory
A7DO_Metabolism = load_module(
    "bridge_metabolism",
    "05_METABOLISM_AND_HOMEOSTASIS/metabolism_master.py",
).A7DO_Metabolism


class BridgeCore:
    def __init__(self):
        self.current_stage = "Gestation"
        self.total_internal_pulses = 0
        self.is_sleeping = False


class CareBridge:
    def __init__(self):
        self.core = BridgeCore()
        self.nervous = A7DO_NervousSystem(self.core)
        self.body = A7DO_Body(self.core)
        self.sensory = A7DO_Sensory(self.core)
        self.metabolism = A7DO_Metabolism(self.core)
        self.care_events = []

    def sync_from_development(self, womb_snapshot: dict, auto_run: bool = False) -> dict:
        self.core.total_internal_pulses = womb_snapshot["biological_days"] * 24
        if womb_snapshot["is_born"]:
            self.core.current_stage = "Neonate" if womb_snapshot["biological_days"] < 320 else "Infancy"
        else:
            self.core.current_stage = "Gestation"

        self.body.update_physical_growth()
        self.nervous.regulate_homeostasis()
        neural_thought = self.nervous.integrate_and_process()

        world_temp = 22.0 if womb_snapshot["is_born"] else 37.0
        self.metabolism.update_metabolic_state(world_temp=world_temp)

        sensory_world = {
            "is_day": True,
            "light_intensity": 80 if womb_snapshot["is_born"] else 12,
            "village_sounds": 42 if womb_snapshot["is_born"] else womb_snapshot["fetal_heartbeat_bpm"],
            "temperature": world_temp,
        }
        perceived = self.sensory.process_external_stimuli(sensory_world)

        care_state = self._apply_care(womb_snapshot, auto_run=auto_run)
        return {
            "stage": self.core.current_stage,
            "neural_report": self.nervous.get_neural_report(),
            "neural_activity": neural_thought,
            "body_status": self.body.get_physical_status(),
            "sensory_status": self.sensory.get_sensory_status(),
            "perception": perceived,
            "metabolic_report": self.metabolism.get_metabolic_report(),
            "care_state": care_state,
            "care_events": self.care_events[-10:],
        }

    def _apply_care(self, womb_snapshot: dict, auto_run: bool) -> dict:
        if not womb_snapshot["is_born"]:
            state = {
                "mode": "maternal_womb_support",
                "feeding": "placental",
                "warmth": "maternal",
                "protection": "uterine",
                "care_active": True,
            }
            self.care_events.append(
                f"Womb care active at {womb_snapshot['mother_location']['label']}."
            )
            self.care_events = self.care_events[-10:]
            return state

        # Postnatal care
        if self.metabolism.energy_reserves < 92:
            self.metabolism.ingest_resource("nutrients", 6.0)
        if self.metabolism.hydration_level < 94:
            self.metabolism.ingest_resource("hydration", 5.0)
        self.metabolism.body_temperature = min(37.0, self.metabolism.body_temperature + 0.05)
        care_event = "Caregiver feeding, warming, and soothing applied."
        if auto_run:
            care_event = "Automatic caregiver cycle maintained feeding, warmth, and regulation."
        self.care_events.append(care_event)
        self.care_events = self.care_events[-10:]
        return {
            "mode": "postnatal_care",
            "feeding": "active",
            "warmth": "blanket_and_skin_contact",
            "protection": "caregiver_supervision",
            "care_active": True,
        }

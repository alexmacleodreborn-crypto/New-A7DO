import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_care_bridge_uses_womb_support_before_birth_and_care_after_birth():
    dev_mod = load(ROOT / "a7do_human_development.py", "human_development_for_care")
    bridge_mod = load(ROOT / "a7do_care_bridge.py", "care_bridge")

    dev = dev_mod.HumanDevelopment(gestational_weeks=10.0, biological_days=70)
    bridge = bridge_mod.CareBridge()

    womb_state = bridge.sync_from_development(dev.snapshot(), auto_run=False)
    assert womb_state["care_state"]["mode"] == "maternal_womb_support"
    assert womb_state["body_status"]["limb_status"] in {"Budding", "Developed"}
    assert "vision" in womb_state["sensory_status"]
    assert "synaptic_density" in womb_state["neural_report"]

    dev.advance_days(220)
    born_state = bridge.sync_from_development(dev.snapshot(), auto_run=True)
    assert born_state["care_state"]["mode"] == "postnatal_care"
    assert born_state["care_state"]["care_active"] is True
    assert born_state["metabolic_report"]["status"] in {"Optimal", "Seeking Resources"}

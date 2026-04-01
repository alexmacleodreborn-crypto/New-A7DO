import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_human_development_starts_in_womb_and_tracks_organs():
    dev_mod = load(ROOT / "a7do_human_development.py", "human_development")
    dev = dev_mod.HumanDevelopment(gestational_weeks=7.43, biological_days=52)

    snap = dev.snapshot()

    assert not snap["is_born"]
    assert snap["state"] in {"embryonic", "fetal_growth", "late_gestation"}
    assert snap["fetal_heartbeat_bpm"] > 0
    assert "spine" in snap["anatomy"]
    assert "brain" in snap["anatomy"]
    assert snap["mother_location"]["gps"]


def test_human_development_auto_birth_and_save(tmp_path):
    dev_mod = load(ROOT / "a7do_human_development.py", "human_development_birth")
    dev = dev_mod.HumanDevelopment(gestational_weeks=39.9, biological_days=279)

    snap = dev.advance_days(2)

    assert snap["is_born"]
    assert snap["state"] == "postnatal"
    assert any("Birth readiness reached" in event for event in snap["recent_events"])

    save_path = tmp_path / "a7do_state.json"
    written = dev.save({"identity": "test-id"}, path=save_path)
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["identity"] == "test-id"
    assert payload["is_born"] is True

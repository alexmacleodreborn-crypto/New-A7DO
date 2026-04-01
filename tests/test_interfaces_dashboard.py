import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dashboard_state_endpoint_works_with_life_loop():
    dash_mod = load(ROOT / "interfaces/dashboard.py", "interfaces_dashboard_test")
    life_mod = load(ROOT / "00_CORE_EXISTENCE/bootstrap/life_loop.py", "life_loop_dash_test")

    life = life_mod.LifeLoop()
    life.tick()

    dash_mod.loop_instance = life
    dash_mod.record_state_snapshot(life)
    state = dash_mod.get_state()

    assert "time" in state
    assert "energy" in state
    assert "strain" in state
    assert "stage" in state
    assert "memory" in state
    assert "history" in state

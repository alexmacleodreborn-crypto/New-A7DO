import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_civilisation_generates_choices_and_story():
    civ_mod = load(ROOT / "a7do_civilisation.py", "civilisation")
    sim = civ_mod.CivilisationSim(seed=3)

    report = sim.step({"weather": "clear", "light": "day"})

    assert report["population"] >= 4
    assert report["story"]
    assert report["dominant_choice"] in {"eat", "rest", "bond", "secure", "learn"}
    assert len(report["citizens"]) == report["population"]
    assert all(citizen["choice"] for citizen in report["citizens"])


def test_life_loop_publishes_civilisation_and_saves_json(tmp_path):
    life_mod = load(
        ROOT / "00_CORE_EXISTENCE/bootstrap/life_loop.py",
        "life_loop_with_civilisation",
    )
    life = life_mod.LifeLoop()

    life.tick()

    snapshot = life.world.snapshot()
    civilisation = snapshot["civilisation"]

    assert civilisation["population"] >= 4
    assert civilisation["story"]
    assert civilisation["resources"]["food"] >= 0.0

    save_path = tmp_path / "a7do_state.json"
    written = life.civilisation.save(
        {
            "identity": life.identity.id,
            "pulse_alive": life.pulse.is_alive(),
            "world_context": civilisation["world_context"],
        },
        path=save_path,
    )

    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["identity"] == life.identity.id
    assert payload["population"] == civilisation["population"]
    assert payload["story"] == life.civilisation.story

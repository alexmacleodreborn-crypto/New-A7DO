from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import random


DATA_PATH = Path(__file__).resolve().parent / "new-A7DO" / "data" / "a7do_state.json"


@dataclass
class Citizen:
    name: str
    role: str
    hunger: float
    safety: float
    curiosity: float
    belonging: float
    wisdom: float
    vitality: float
    last_choice: str = "wake"
    last_reason: str = "beginning life in the settlement"

    def choose_action(self, resources: dict[str, float], weather: str) -> tuple[str, str]:
        pressures = {
            "eat": 1.0 - self.hunger,
            "rest": 1.0 - self.vitality,
            "bond": 1.0 - self.belonging,
            "secure": 1.0 - min(self.safety, resources["security"]),
            "learn": self.curiosity,
        }
        action = max(pressures, key=pressures.get)

        role_bias = {
            "Grower": "eat",
            "Builder": "secure",
            "Thinker": "learn",
            "Carer": "bond",
        }.get(self.role)

        if role_bias and pressures[role_bias] >= pressures[action] - 0.15:
            action = role_bias

        if weather == "storm" and action == "learn":
            action = "secure"

        reasons = {
            "eat": "food stores feel too low for comfort",
            "rest": "the body needs recovery before it can help others",
            "bond": "the settlement needs trust to stay alive",
            "secure": "danger feels close and the village needs protection",
            "learn": "curiosity is pulling life toward discovery",
        }
        return action, reasons[action]


@dataclass
class CivilisationSim:
    seed: int = 7
    tick_count: int = 0
    season_index: int = 0
    resources: dict[str, float] = field(default_factory=dict)
    citizens: list[Citizen] = field(default_factory=list)
    recent_events: list[str] = field(default_factory=list)
    dilemmas: list[str] = field(default_factory=list)
    story: str = "The settlement is waiting for its first decision."
    rng: random.Random = field(init=False, repr=False)

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        if not self.resources:
            self.resources = {
                "food": 0.62,
                "materials": 0.48,
                "knowledge": 0.28,
                "culture": 0.35,
                "security": 0.51,
                "spirit": 0.55,
            }
        if not self.citizens:
            self.citizens = [
                Citizen("Ari", "Grower", 0.66, 0.54, 0.32, 0.61, 0.26, 0.74),
                Citizen("Mira", "Builder", 0.59, 0.58, 0.41, 0.47, 0.38, 0.68),
                Citizen("Sol", "Thinker", 0.52, 0.49, 0.73, 0.44, 0.62, 0.57),
                Citizen("Tala", "Carer", 0.63, 0.52, 0.39, 0.76, 0.41, 0.71),
            ]

    @property
    def season(self) -> str:
        return ["Seed", "Bloom", "Harvest", "Ash"][self.season_index % 4]

    def step(self, world_context: dict | None = None) -> dict:
        world_context = world_context or {}
        self.tick_count += 1
        if self.tick_count % 6 == 0:
            self.season_index += 1

        weather = world_context.get("weather", "clear")
        light = world_context.get("light", "day")

        citizen_reports = []
        for citizen in self.citizens:
            action, reason = citizen.choose_action(self.resources, weather)
            citizen.last_choice = action
            citizen.last_reason = reason
            self._apply_choice(citizen, action, weather, light)
            citizen_reports.append(
                {
                    "name": citizen.name,
                    "role": citizen.role,
                    "choice": action,
                    "reason": reason,
                    "vitality": round(citizen.vitality, 2),
                    "hunger": round(citizen.hunger, 2),
                    "belonging": round(citizen.belonging, 2),
                    "curiosity": round(citizen.curiosity, 2),
                }
            )

        self._nudge_resources(weather)
        self.dilemmas = self._build_dilemmas(weather)
        self.story = self._build_story(weather, citizen_reports)
        self.recent_events.append(self.story)
        self.recent_events = self.recent_events[-8:]

        report = self.report(world_context=world_context)
        report["citizens"] = citizen_reports
        return report

    def _apply_choice(self, citizen: Citizen, action: str, weather: str, light: str) -> None:
        if action == "eat":
            self.resources["food"] = max(0.0, self.resources["food"] - 0.07)
            citizen.hunger = min(1.0, citizen.hunger + 0.16)
            citizen.vitality = min(1.0, citizen.vitality + 0.05)
        elif action == "rest":
            citizen.vitality = min(1.0, citizen.vitality + 0.18)
            citizen.safety = min(1.0, citizen.safety + 0.03)
        elif action == "bond":
            self.resources["culture"] = min(1.0, self.resources["culture"] + 0.08)
            self.resources["spirit"] = min(1.0, self.resources["spirit"] + 0.07)
            citizen.belonging = min(1.0, citizen.belonging + 0.14)
        elif action == "secure":
            self.resources["security"] = min(1.0, self.resources["security"] + 0.11)
            self.resources["materials"] = max(0.0, self.resources["materials"] - 0.04)
            citizen.safety = min(1.0, citizen.safety + 0.12)
        elif action == "learn":
            self.resources["knowledge"] = min(1.0, self.resources["knowledge"] + 0.10)
            citizen.curiosity = max(0.0, citizen.curiosity - 0.08)
            citizen.wisdom = min(1.0, citizen.wisdom + 0.08)

        if citizen.role == "Grower":
            self.resources["food"] = min(1.0, self.resources["food"] + 0.09)
        elif citizen.role == "Builder":
            self.resources["materials"] = min(1.0, self.resources["materials"] + 0.05)
        elif citizen.role == "Thinker":
            self.resources["knowledge"] = min(1.0, self.resources["knowledge"] + 0.04)
        elif citizen.role == "Carer":
            self.resources["spirit"] = min(1.0, self.resources["spirit"] + 0.05)

        citizen.hunger = max(0.0, citizen.hunger - 0.03)
        citizen.vitality = max(0.0, citizen.vitality - 0.04)
        citizen.belonging = max(0.0, citizen.belonging - 0.01)
        if weather == "storm":
            citizen.safety = max(0.0, citizen.safety - 0.05)
        if light == "night":
            citizen.curiosity = min(1.0, citizen.curiosity + 0.03)

    def _nudge_resources(self, weather: str) -> None:
        self.resources["food"] = max(0.0, min(1.0, self.resources["food"] - 0.02))
        self.resources["spirit"] = max(0.0, min(1.0, self.resources["spirit"] - 0.01))
        if weather == "storm":
            self.resources["security"] = max(0.0, self.resources["security"] - 0.04)
        else:
            self.resources["materials"] = min(1.0, self.resources["materials"] + 0.01)

    def _build_dilemmas(self, weather: str) -> list[str]:
        dilemmas = []
        if self.resources["food"] < 0.4:
            dilemmas.append("Food is thinning. The village must trade comfort for survival.")
        if self.resources["security"] < 0.45 or weather == "storm":
            dilemmas.append("Safety feels fragile. Work can go to shelter or to discovery.")
        if self.resources["knowledge"] > 0.55 and self.resources["materials"] > 0.4:
            dilemmas.append("New ideas are ready. The village can risk building something lasting.")
        if not dilemmas:
            dilemmas.append("Life is stable enough for choice, but every calm season hides a future cost.")
        return dilemmas

    def _build_story(self, weather: str, citizen_reports: list[dict]) -> str:
        lead = max(
            citizen_reports,
            key=lambda item: {
                "eat": 1,
                "rest": 2,
                "bond": 3,
                "secure": 4,
                "learn": 5,
            }[item["choice"]],
        )
        return (
            f"Tick {self.tick_count}: In {self.season} season under {weather} skies, "
            f"{lead['name']} the {lead['role']} chose to {lead['choice']} because {lead['reason']}."
        )

    def report(self, world_context: dict | None = None) -> dict:
        world_context = world_context or {}
        population = len(self.citizens)
        avg_wisdom = sum(c.wisdom for c in self.citizens) / population
        dominant_choice = max(
            ("eat", "rest", "bond", "secure", "learn"),
            key=lambda choice: sum(1 for c in self.citizens if c.last_choice == choice),
        )
        return {
            "tick": self.tick_count,
            "season": self.season,
            "population": population,
            "dominant_choice": dominant_choice,
            "resources": {key: round(value, 2) for key, value in self.resources.items()},
            "avg_wisdom": round(avg_wisdom, 2),
            "dilemmas": list(self.dilemmas),
            "story": self.story,
            "recent_events": list(self.recent_events),
            "world_context": world_context,
            "citizens": [
                {
                    "name": c.name,
                    "role": c.role,
                    "choice": c.last_choice,
                    "reason": c.last_reason,
                    "vitality": round(c.vitality, 2),
                    "hunger": round(c.hunger, 2),
                    "belonging": round(c.belonging, 2),
                    "curiosity": round(c.curiosity, 2),
                }
                for c in self.citizens
            ],
        }

    def save(self, extra_state: dict | None = None, path: Path | None = None) -> Path:
        payload = self.report(world_context=(extra_state or {}).get("world_context"))
        if extra_state:
            payload.update(extra_state)
        save_path = path or DATA_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return save_path

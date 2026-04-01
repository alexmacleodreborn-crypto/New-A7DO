from __future__ import annotations

from pathlib import Path
import json
import random


DATA_PATH = Path(__file__).resolve().parent / "new-A7DO" / "data" / "a7do_state.json"


WORLD_NODES = {
    "house_01": {
        "label": "Ari House",
        "kind": "house",
        "x": 0,
        "y": 0,
        "z": 0,
        "connections": ["street_01"],
    },
    "house_02": {
        "label": "Mira House",
        "kind": "house",
        "x": 2,
        "y": 0,
        "z": 0,
        "connections": ["street_01"],
    },
    "house_03": {
        "label": "Shared House",
        "kind": "house",
        "x": 4,
        "y": 0,
        "z": 0,
        "connections": ["street_01"],
    },
    "street_01": {
        "label": "Main Street",
        "kind": "street",
        "x": 2,
        "y": 1,
        "z": 0,
        "connections": ["house_01", "house_02", "house_03", "market_01", "park_01", "plaza_01"],
    },
    "market_01": {
        "label": "Market",
        "kind": "market",
        "x": 5,
        "y": 2,
        "z": 0,
        "connections": ["street_01"],
    },
    "park_01": {
        "label": "Park",
        "kind": "park",
        "x": 0,
        "y": 3,
        "z": 1,
        "connections": ["street_01", "plaza_01"],
    },
    "plaza_01": {
        "label": "3D Spatial Plaza",
        "kind": "plaza",
        "x": 3,
        "y": 4,
        "z": 2,
        "connections": ["street_01", "park_01", "learning_01"],
    },
    "learning_01": {
        "label": "Language Hub",
        "kind": "learning_center",
        "x": 6,
        "y": 4,
        "z": 1,
        "connections": ["plaza_01"],
    },
}


class Citizen:
    def __init__(
        self,
        name: str,
        role: str,
        hunger: float,
        safety: float,
        curiosity: float,
        belonging: float,
        wisdom: float,
        vitality: float,
        home: str,
    ):
        self.name = name
        self.role = role
        self.hunger = hunger
        self.safety = safety
        self.curiosity = curiosity
        self.belonging = belonging
        self.wisdom = wisdom
        self.vitality = vitality
        self.home = home
        self.location = home
        self.last_choice = "wake"
        self.last_reason = "beginning life in the settlement"
        self.last_conversation = ""

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


class CivilisationSim:
    def __init__(self, seed: int = 7):
        self.seed = seed
        self.tick_count = 0
        self.season_index = 0
        self.rng = random.Random(seed)
        self.resources = {
            "food": 0.62,
            "materials": 0.48,
            "knowledge": 0.28,
            "culture": 0.35,
            "security": 0.51,
            "spirit": 0.55,
        }
        self.citizens = [
            Citizen("Ari", "Grower", 0.66, 0.54, 0.32, 0.61, 0.26, 0.74, "house_01"),
            Citizen("Mira", "Builder", 0.59, 0.58, 0.41, 0.47, 0.38, 0.68, "house_02"),
            Citizen("Sol", "Thinker", 0.52, 0.49, 0.73, 0.44, 0.62, 0.57, "house_03"),
            Citizen("Tala", "Carer", 0.63, 0.52, 0.39, 0.76, 0.41, 0.71, "house_03"),
        ]
        self.world_frame = dict(WORLD_NODES)
        self.recent_events = []
        self.dilemmas = []
        self.story = "The settlement is waiting for its first decision."
        self.recent_conversations = []

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
            citizen.location = self._pick_destination(citizen, action, weather, light)
            self._apply_choice(citizen, action, weather, light)
            citizen_reports.append(self._citizen_report(citizen))

        self._nudge_resources(weather)
        self.recent_conversations = self._build_conversations()
        self.dilemmas = self._build_dilemmas(weather)
        self.story = self._build_story(weather, citizen_reports)
        self.recent_events.append(self.story)
        for convo in self.recent_conversations:
            self.recent_events.append(convo["summary"])
        self.recent_events = self.recent_events[-10:]

        report = self.report(world_context=world_context)
        report["citizens"] = citizen_reports
        return report

    def _pick_destination(self, citizen: Citizen, action: str, weather: str, light: str) -> str:
        if weather == "storm":
            return citizen.home
        if action == "eat":
            return "market_01" if self.resources["food"] < 0.75 else citizen.home
        if action == "rest":
            return citizen.home if light == "night" else "park_01"
        if action == "bond":
            return "plaza_01" if light == "day" else "house_03"
        if action == "secure":
            return "street_01"
        if action == "learn":
            return "learning_01" if light == "day" else "plaza_01"
        return citizen.home

    def _citizen_report(self, citizen: Citizen) -> dict:
        node = self.world_frame[citizen.location]
        return {
            "name": citizen.name,
            "role": citizen.role,
            "choice": citizen.last_choice,
            "reason": citizen.last_reason,
            "location": citizen.location,
            "location_label": node["label"],
            "xyz": [node["x"], node["y"], node["z"]],
            "vitality": round(citizen.vitality, 2),
            "hunger": round(citizen.hunger, 2),
            "belonging": round(citizen.belonging, 2),
            "curiosity": round(citizen.curiosity, 2),
            "conversation": citizen.last_conversation,
        }

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

    def _build_conversations(self) -> list[dict]:
        by_place = {}
        for citizen in self.citizens:
            citizen.last_conversation = ""
            by_place.setdefault(citizen.location, []).append(citizen)

        conversations = []
        topics = {
            "eat": "food and trade",
            "rest": "recovery and safety",
            "bond": "trust and family",
            "secure": "shelter and defense",
            "learn": "maps, symbols, and the shape of the world",
        }
        for place_id, people in by_place.items():
            if len(people) < 2:
                continue
            speaker_a = people[0]
            speaker_b = people[1]
            topic = topics.get(speaker_a.last_choice, "daily life")
            line_a = f"{speaker_a.name}: We should focus on {topic}."
            line_b = f"{speaker_b.name}: I agree, but the village must choose carefully."
            summary = f"At {self.world_frame[place_id]['label']}, {speaker_a.name} and {speaker_b.name} talked about {topic}."
            speaker_a.last_conversation = line_a
            speaker_b.last_conversation = line_b
            conversations.append(
                {
                    "place_id": place_id,
                    "place_label": self.world_frame[place_id]["label"],
                    "participants": [speaker_a.name, speaker_b.name],
                    "topic": topic,
                    "lines": [line_a, line_b],
                    "summary": summary,
                }
            )
        return conversations[-4:]

    def _spatial_frame(self) -> dict:
        occupancy = {place_id: [] for place_id in self.world_frame}
        for citizen in self.citizens:
            occupancy[citizen.location].append(citizen.name)

        nodes = []
        for place_id, node in self.world_frame.items():
            nodes.append(
                {
                    "place_id": place_id,
                    "label": node["label"],
                    "kind": node["kind"],
                    "x": node["x"],
                    "y": node["y"],
                    "z": node["z"],
                    "occupants": occupancy[place_id],
                    "occupant_count": len(occupancy[place_id]),
                    "connections": node["connections"],
                }
            )
        return {
            "bounds": {"x": [0, 6], "y": [0, 4], "z": [0, 2]},
            "nodes": nodes,
        }

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
        if self.recent_conversations:
            dilemmas.append("Conversation is changing the settlement's choices across homes, streets, and the plaza.")
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
            f"{lead['name']} the {lead['role']} moved to {lead['location_label']} "
            f"at {tuple(lead['xyz'])} and chose to {lead['choice']} because {lead['reason']}."
        )

    def report(self, world_context: dict | None = None) -> dict:
        world_context = world_context or {}
        population = len(self.citizens)
        avg_wisdom = sum(c.wisdom for c in self.citizens) / population
        dominant_choice = max(
            ("eat", "rest", "bond", "secure", "learn"),
            key=lambda choice: sum(1 for c in self.citizens if c.last_choice == choice),
        )
        houses = [node for node in self._spatial_frame()["nodes"] if node["kind"] == "house"]
        return {
            "tick": self.tick_count,
            "season": self.season,
            "population": population,
            "dominant_choice": dominant_choice,
            "resources": {key: round(value, 2) for key, value in self.resources.items()},
            "avg_wisdom": round(avg_wisdom, 2),
            "house_count": len(houses),
            "dilemmas": list(self.dilemmas),
            "story": self.story,
            "recent_events": list(self.recent_events),
            "recent_conversations": list(self.recent_conversations),
            "world_context": world_context,
            "spatial_frame": self._spatial_frame(),
            "citizens": [self._citizen_report(citizen) for citizen in self.citizens],
        }

    def save(self, extra_state: dict | None = None, path: Path | None = None) -> Path:
        payload = self.report(world_context=(extra_state or {}).get("world_context"))
        if extra_state:
            payload.update(extra_state)
        save_path = path or DATA_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return save_path

from __future__ import annotations

from pathlib import Path
import json
import random


DATA_PATH = Path(__file__).resolve().parent / "new-A7DO" / "data" / "a7do_state.json"


WORLD_NODES = {
    "house_01": {"label": "Ari House", "kind": "house", "x": 0, "y": 0, "z": 0, "connections": ["street_01"]},
    "house_02": {"label": "Mira House", "kind": "house", "x": 2, "y": 0, "z": 0, "connections": ["street_01"]},
    "house_03": {"label": "Shared House", "kind": "house", "x": 4, "y": 0, "z": 0, "connections": ["street_01"]},
    "house_04": {"label": "Neighbour House", "kind": "house", "x": 6, "y": 0, "z": 0, "connections": ["street_01"]},
    "street_01": {"label": "Main Street", "kind": "street", "x": 3, "y": 1, "z": 0, "connections": ["house_01", "house_02", "house_03", "house_04", "market_01", "park_01", "school_01", "work_01", "road_01"]},
    "road_01": {"label": "Village Road", "kind": "road", "x": 5, "y": 1, "z": 0, "connections": ["street_01", "park_02", "work_01"]},
    "market_01": {"label": "Market", "kind": "market", "x": 6, "y": 2, "z": 0, "connections": ["street_01"]},
    "park_01": {"label": "Neighbourhood Park", "kind": "park", "x": 0, "y": 3, "z": 1, "connections": ["street_01", "plaza_01"]},
    "park_02": {"label": "Play Park", "kind": "park", "x": 7, "y": 3, "z": 1, "connections": ["road_01"]},
    "school_01": {"label": "Primary School", "kind": "school", "x": 2, "y": 4, "z": 0, "connections": ["street_01", "plaza_01"]},
    "work_01": {"label": "Workplace", "kind": "workplace", "x": 7, "y": 4, "z": 0, "connections": ["road_01"]},
    "plaza_01": {"label": "3D Spatial Plaza", "kind": "plaza", "x": 4, "y": 5, "z": 2, "connections": ["park_01", "school_01", "learning_01"]},
    "learning_01": {"label": "Learning Hub", "kind": "learning_center", "x": 6, "y": 5, "z": 1, "connections": ["plaza_01"]},
}

SCENARIOS = [
    "quiet_school_morning",
    "park_playtime",
    "market_day",
    "commute_and_work",
    "rainy_neighbourhood_evening",
]


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
            "Student": "learn",
            "Worker": "secure",
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
            Citizen("Noah", "Worker", 0.61, 0.57, 0.31, 0.53, 0.35, 0.7, "house_04"),
            Citizen("Lina", "Student", 0.64, 0.55, 0.67, 0.62, 0.29, 0.73, "house_04"),
        ]
        self.world_frame = dict(WORLD_NODES)
        self.recent_events = []
        self.dilemmas = []
        self.story = "The settlement is waiting for its first decision."
        self.recent_conversations = []
        self.cars = [
            {"id": "car_01", "route": ["road_01", "street_01", "market_01"], "route_index": 0},
            {"id": "car_02", "route": ["road_01", "work_01", "street_01"], "route_index": 0},
        ]
        self.a7do_member = None

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
        self._sync_a7do_member(world_context.get("a7do_profile"))

        citizen_reports = []
        for citizen in self.citizens:
            action, reason = citizen.choose_action(self.resources, weather)
            if citizen.name == "A7DO" and self.a7do_member is not None:
                action, reason = self._choose_a7do_path(world_context.get("a7do_profile", {}), weather, light)
            citizen.last_choice = action
            citizen.last_reason = reason
            citizen.location = self._pick_destination(citizen, action, weather, light, world_context.get("a7do_profile", {}))
            self._apply_choice(citizen, action, weather, light)
            citizen_reports.append(self._citizen_report(citizen))

        self._advance_cars()
        self._nudge_resources(weather)
        self.recent_conversations = self._build_conversations()
        self.dilemmas = self._build_dilemmas(weather, world_context.get("a7do_profile", {}))
        self.story = self._build_story(weather, citizen_reports)
        self.recent_events.append(self.story)
        self.recent_events.extend(convo["summary"] for convo in self.recent_conversations)
        self.recent_events.extend(self._car_events())
        self.recent_events = self.recent_events[-14:]

        report = self.report(world_context=world_context)
        report["citizens"] = citizen_reports
        return report

    def _sync_a7do_member(self, profile: dict | None) -> None:
        profile = profile or {}
        if not profile.get("is_born"):
            self.citizens = [citizen for citizen in self.citizens if citizen.name != "A7DO"]
            self.a7do_member = None
            return
        if self.a7do_member is None:
            self.a7do_member = Citizen("A7DO", "Student", 0.7, 0.6, 0.8, 0.52, 0.18, 0.65, "house_03")
            self.citizens.append(self.a7do_member)
        else:
            self.a7do_member.role = "Worker" if profile.get("workplace_ready") else "Student"
            self.a7do_member.curiosity = min(1.0, 0.3 + profile.get("vision_progress", 0.0) * 0.5 + profile.get("smell_progress", 0.0) * 0.2)
            self.a7do_member.wisdom = min(1.0, 0.15 + profile.get("speech_progress", 0.0) * 0.45)

    def _choose_a7do_path(self, profile: dict, weather: str, light: str) -> tuple[str, str]:
        if profile.get("workplace_ready"):
            return "secure", "daily work and responsibility are now part of life"
        if profile.get("school_ready"):
            return "learn", "school attendance is part of growing into the community"
        if profile.get("speech_progress", 0.0) < 0.2:
            return "bond", "care and attachment come before formal schooling"
        if profile.get("vision_progress", 0.0) < 0.5 or profile.get("smell_progress", 0.0) < 0.5:
            return "learn", "the senses are opening and the world is becoming understandable"
        return "bond", "play and social learning are shaping development"

    def _pick_destination(self, citizen: Citizen, action: str, weather: str, light: str, a7do_profile: dict) -> str:
        if weather == "storm":
            return citizen.home
        if citizen.name == "A7DO":
            if a7do_profile.get("workplace_ready"):
                return "work_01"
            if a7do_profile.get("school_ready"):
                return "school_01"
            if a7do_profile.get("life_phase") in {"child", "toddler"}:
                return "park_02"
            return citizen.home if light == "night" else "park_01"
        if action == "eat":
            return "market_01" if self.resources["food"] < 0.75 else citizen.home
        if action == "rest":
            return citizen.home if light == "night" else "park_01"
        if action == "bond":
            return "plaza_01" if light == "day" else "house_03"
        if action == "secure":
            return "street_01" if citizen.role != "Worker" else "work_01"
        if action == "learn":
            return "school_01" if citizen.role == "Student" else "learning_01"
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
            citizen.curiosity = max(0.0, citizen.curiosity - 0.05)
            citizen.wisdom = min(1.0, citizen.wisdom + 0.05)
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
            "learn": "school, symbols, and neighbourhood life",
        }
        for place_id, people in by_place.items():
            if len(people) < 2:
                continue
            speaker_a = people[0]
            speaker_b = people[1]
            topic = topics.get(speaker_a.last_choice, "daily life")
            if "A7DO" in {speaker_a.name, speaker_b.name}:
                topic = "school, play, and growing senses"
            line_a = f"{speaker_a.name}: We should focus on {topic}."
            line_b = f"{speaker_b.name}: I agree, and the neighbourhood will shape us."
            summary = f"At {self.world_frame[place_id]['label']}, {speaker_a.name} and {speaker_b.name} talked about {topic}."
            speaker_a.last_conversation = line_a
            speaker_b.last_conversation = line_b
            conversations.append({"place_id": place_id, "place_label": self.world_frame[place_id]["label"], "participants": [speaker_a.name, speaker_b.name], "topic": topic, "lines": [line_a, line_b], "summary": summary})
        return conversations[-6:]

    def _advance_cars(self) -> None:
        for car in self.cars:
            car["route_index"] = (car["route_index"] + 1) % len(car["route"])

    def _car_events(self) -> list[str]:
        events = []
        for car in self.cars:
            current = car["route"][car["route_index"]]
            events.append(f"{car['id']} moved through {self.world_frame[current]['label']}.")
        return events

    def _spatial_frame(self) -> dict:
        occupancy = {place_id: [] for place_id in self.world_frame}
        for citizen in self.citizens:
            occupancy[citizen.location].append(citizen.name)
        nodes = []
        for place_id, node in self.world_frame.items():
            nodes.append({"place_id": place_id, "label": node["label"], "kind": node["kind"], "x": node["x"], "y": node["y"], "z": node["z"], "occupants": occupancy[place_id], "occupant_count": len(occupancy[place_id]), "connections": node["connections"]})
        vehicles = []
        for car in self.cars:
            loc = car["route"][car["route_index"]]
            node = self.world_frame[loc]
            vehicles.append({"id": car["id"], "location": loc, "label": node["label"], "xyz": [node["x"], node["y"], node["z"]]})
        return {"bounds": {"x": [0, 7], "y": [0, 5], "z": [0, 2]}, "nodes": nodes, "vehicles": vehicles}

    def _nudge_resources(self, weather: str) -> None:
        self.resources["food"] = max(0.0, min(1.0, self.resources["food"] - 0.02))
        self.resources["spirit"] = max(0.0, min(1.0, self.resources["spirit"] - 0.01))
        if weather == "storm":
            self.resources["security"] = max(0.0, self.resources["security"] - 0.04)
        else:
            self.resources["materials"] = min(1.0, self.resources["materials"] + 0.01)

    def _build_dilemmas(self, weather: str, a7do_profile: dict) -> list[str]:
        dilemmas = []
        if self.resources["food"] < 0.4:
            dilemmas.append("Food is thinning. The village must trade comfort for survival.")
        if self.resources["security"] < 0.45 or weather == "storm":
            dilemmas.append("Safety feels fragile. Work can go to shelter or to discovery.")
        if a7do_profile.get("school_ready") and not a7do_profile.get("workplace_ready"):
            dilemmas.append("A7DO is old enough for school, and the neighbourhood is shaping daily learning.")
        if a7do_profile.get("workplace_ready"):
            dilemmas.append("A7DO is old enough for work, and adult responsibility now competes with curiosity.")
        dilemmas.append(f"Scenario active: {SCENARIOS[self.tick_count % len(SCENARIOS)]}.")
        return dilemmas[-5:]

    def _build_story(self, weather: str, citizen_reports: list[dict]) -> str:
        lead = max(citizen_reports, key=lambda item: {"eat": 1, "rest": 2, "bond": 3, "secure": 4, "learn": 5}[item["choice"]])
        return (
            f"Tick {self.tick_count}: In {self.season} season under {weather} skies, "
            f"{lead['name']} the {lead['role']} moved to {lead['location_label']} "
            f"at {tuple(lead['xyz'])} and chose to {lead['choice']} because {lead['reason']}."
        )

    def report(self, world_context: dict | None = None) -> dict:
        world_context = world_context or {}
        self._sync_a7do_member(world_context.get("a7do_profile"))
        population = len(self.citizens)
        avg_wisdom = sum(c.wisdom for c in self.citizens) / population
        dominant_choice = max(("eat", "rest", "bond", "secure", "learn"), key=lambda choice: sum(1 for c in self.citizens if c.last_choice == choice))
        spatial = self._spatial_frame()
        houses = [node for node in spatial["nodes"] if node["kind"] == "house"]
        return {
            "tick": self.tick_count,
            "season": self.season,
            "population": population,
            "dominant_choice": dominant_choice,
            "resources": {key: round(value, 2) for key, value in self.resources.items()},
            "avg_wisdom": round(avg_wisdom, 2),
            "house_count": len(houses),
            "scenario": SCENARIOS[self.tick_count % len(SCENARIOS)],
            "dilemmas": list(self.dilemmas),
            "story": self.story,
            "recent_events": list(self.recent_events),
            "recent_conversations": list(self.recent_conversations),
            "world_context": world_context,
            "spatial_frame": spatial,
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

from __future__ import annotations

from pathlib import Path
import json


DATA_PATH = Path(__file__).resolve().parent / "new-A7DO" / "data" / "a7do_state.json"


MOTHER_WORLD = {
    "home": {"label": "Family Home", "x": 0, "y": 0, "z": 0, "lat": 51.5007, "lon": -0.1246},
    "clinic": {"label": "Prenatal Clinic", "x": 3, "y": 1, "z": 0, "lat": 51.5014, "lon": -0.1232},
    "market": {"label": "Market", "x": 5, "y": 2, "z": 0, "lat": 51.5021, "lon": -0.1224},
    "park": {"label": "Riverside Park", "x": 1, "y": 4, "z": 1, "lat": 51.5010, "lon": -0.1255},
    "street": {"label": "Main Street", "x": 2, "y": 2, "z": 0, "lat": 51.5017, "lon": -0.1239},
    "hospital": {"label": "Birth Hospital", "x": 4, "y": 0, "z": 0, "lat": 51.5009, "lon": -0.1218},
}

MOTHER_ROUTE = ["home", "street", "market", "street", "park", "street", "clinic", "home"]


class HumanDevelopment:
    def __init__(self, gestational_weeks: float = 7.43, biological_days: int = 52):
        self.gestational_weeks = gestational_weeks
        self.biological_days = biological_days
        self.birth_weeks = 40.0
        self.is_born = self.gestational_weeks >= self.birth_weeks
        self.birth_logged = self.is_born
        self.route_index = 0
        self.mother_location = MOTHER_ROUTE[self.route_index]
        self.recent_events = []

    def advance_days(self, days: int = 1) -> dict:
        for _ in range(days):
            self.biological_days += 1
            self.gestational_weeks += 1.0 / 7.0
            self.route_index = (self.route_index + 1) % len(MOTHER_ROUTE)
            self.mother_location = MOTHER_ROUTE[self.route_index]
            self.recent_events.append(
                f"Day {self.biological_days}: Mother moved to {self.current_building()['label']}."
            )
            if not self.is_born and self.gestational_weeks >= self.birth_weeks:
                self.is_born = True
                self.recent_events.append(
                    f"Day {self.biological_days}: Birth readiness reached at {self.current_building()['label']}."
                )
        self.recent_events = self.recent_events[-12:]
        return self.snapshot()

    def trimester(self) -> int:
        if self.gestational_weeks < 13:
            return 1
        if self.gestational_weeks < 27:
            return 2
        return 3

    def current_building(self) -> dict:
        return MOTHER_WORLD[self.mother_location]

    def womb_state(self) -> str:
        if self.is_born:
            return "postnatal"
        if self.gestational_weeks < 8:
            return "embryonic"
        if self.gestational_weeks < 24:
            return "fetal_growth"
        return "late_gestation"

    def fetal_heartbeat_bpm(self) -> int:
        if self.gestational_weeks < 5:
            return 0
        if self.gestational_weeks < 9:
            return int(90 + (self.gestational_weeks - 5) * 20)
        if self.gestational_weeks < 20:
            return int(150 - (self.gestational_weeks - 9) * 1.5)
        return int(135 - min(20, self.gestational_weeks - 20) * 0.4)

    def anatomical_growth(self) -> dict:
        weeks = self.gestational_weeks
        return {
            "spine": self._phase_value(weeks, 4, 38),
            "skull": self._phase_value(weeks, 5, 37),
            "brain": self._phase_value(weeks, 5, 40),
            "heart": self._phase_value(weeks, 4.5, 28),
            "heartbeat": self._phase_value(weeks, 5, 12),
            "arms": self._phase_value(weeks, 6, 24),
            "legs": self._phase_value(weeks, 6, 24),
            "hands": self._phase_value(weeks, 8, 24),
            "feet": self._phase_value(weeks, 8, 24),
            "lungs": self._phase_value(weeks, 16, 39),
            "senses": self._phase_value(weeks, 18, 34),
        }

    def postnatal_profile(self) -> dict:
        postnatal_days = max(0, self.biological_days - int(self.birth_weeks * 7))
        age_years = round(postnatal_days / 365.0, 2)
        speech_progress = min(1.0, postnatal_days / 720.0)
        smell_progress = min(1.0, postnatal_days / 180.0)
        vision_progress = min(1.0, 0.2 + postnatal_days / 365.0)
        school_ready = postnatal_days >= 365 * 4
        workplace_ready = postnatal_days >= 365 * 18
        life_phase = "newborn"
        if postnatal_days >= 365 * 2:
            life_phase = "toddler"
        if postnatal_days >= 365 * 5:
            life_phase = "child"
        if postnatal_days >= 365 * 13:
            life_phase = "adolescent"
        if postnatal_days >= 365 * 18:
            life_phase = "adult"

        if speech_progress < 0.15:
            speech_stage = "crying_only"
        elif speech_progress < 0.35:
            speech_stage = "babbling"
        elif speech_progress < 0.65:
            speech_stage = "single_words"
        elif speech_progress < 0.9:
            speech_stage = "short_sentences"
        else:
            speech_stage = "fluent_speech"

        return {
            "postnatal_days": postnatal_days,
            "age_years": age_years,
            "life_phase": life_phase,
            "speech_stage": speech_stage,
            "speech_progress": round(speech_progress, 2),
            "smell_progress": round(smell_progress, 2),
            "vision_progress": round(vision_progress, 2),
            "school_ready": school_ready,
            "workplace_ready": workplace_ready,
        }

    def _phase_value(self, weeks: float, start: float, end: float) -> dict:
        if weeks < start:
            progress = 0.0
            stage = "not_started"
        elif weeks >= end:
            progress = 1.0
            stage = "ready"
        else:
            progress = (weeks - start) / (end - start)
            if progress < 0.33:
                stage = "forming"
            elif progress < 0.66:
                stage = "developing"
            else:
                stage = "maturing"
        return {"progress": round(progress, 2), "stage": stage}

    def mother_motion_vector(self) -> dict:
        current = self.current_building()
        next_id = MOTHER_ROUTE[(self.route_index + 1) % len(MOTHER_ROUTE)]
        nxt = MOTHER_WORLD[next_id]
        return {
            "from": self.mother_location,
            "to": next_id,
            "dx": nxt["x"] - current["x"],
            "dy": nxt["y"] - current["y"],
            "dz": nxt["z"] - current["z"],
        }

    def snapshot(self) -> dict:
        building = self.current_building()
        anatomy = self.anatomical_growth()
        return {
            "gestational_weeks": round(self.gestational_weeks, 2),
            "biological_days": self.biological_days,
            "trimester": self.trimester(),
            "state": self.womb_state(),
            "is_born": self.is_born,
            "fetal_heartbeat_bpm": self.fetal_heartbeat_bpm(),
            "mother_location": {
                "place_id": self.mother_location,
                "label": building["label"],
                "xyz": [building["x"], building["y"], building["z"]],
                "gps": [building["lat"], building["lon"]],
            },
            "mother_motion": self.mother_motion_vector(),
            "buildings": [
                {
                    "place_id": place_id,
                    "label": place["label"],
                    "xyz": [place["x"], place["y"], place["z"]],
                    "gps": [place["lat"], place["lon"]],
                }
                for place_id, place in MOTHER_WORLD.items()
            ],
            "anatomy": anatomy,
            "postnatal_profile": self.postnatal_profile(),
            "recent_events": list(self.recent_events),
        }

    def save(self, extra_state: dict | None = None, path: Path | None = None) -> Path:
        payload = self.snapshot()
        if extra_state:
            payload.update(extra_state)
        save_path = path or DATA_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return save_path

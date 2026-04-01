"""
A7DO — Live Introspection Dashboard
Manual Tick Control (Authoritative Time Boundary)
"""

import importlib.util
import math
import random
import re
import time
from types import SimpleNamespace

import streamlit as st
from pathlib import Path

from english_core_curriculum import run_core_english_curriculum
# --------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent

def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# --------------------------------------------------
# LOAD WORLD
# --------------------------------------------------
world_time_mod = load_module("world_time", "09_WORLD_MODEL/time.py")
world_state_mod = load_module("world_state", "09_WORLD_MODEL/world_state.py")
world_env_mod = load_module("world_env", "09_WORLD_MODEL/environments/world.py")

WorldTime = world_time_mod.WorldTime
WorldState = world_state_mod.WorldState
World = world_env_mod.World

# --------------------------------------------------
# LOAD LIFE LOOP
# --------------------------------------------------
life_loop_mod = load_module(
    "life_loop",
    "00_CORE_EXISTENCE/bootstrap/life_loop.py"
)
LifeLoop = life_loop_mod.LifeLoop
life_stages_mod = load_module(
    "life_stages",
    "00_CORE_EXISTENCE/lifecycle/stages.py",
)
HumanDevelopment = load_module(
    "human_development",
    "a7do_human_development.py",
).HumanDevelopment
CareBridge = load_module(
    "care_bridge",
    "a7do_care_bridge.py",
).CareBridge
LifeStage = life_stages_mod.LifeStage

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "life" not in st.session_state:
    world_time = WorldTime()
    world_state = WorldState(default_place="house")
    st.session_state.world_env = World.create(world_state=world_state)
    st.session_state.life = LifeLoop(
        world_time,
        world_state,
        stage_schedule=[
            (0, LifeStage.WOMB),
            (1, LifeStage.BIRTH),
            (120, LifeStage.INFANT),
            (600, LifeStage.TODDLER),
        ],
    )

if "run_ticks_remaining" not in st.session_state:
    st.session_state.run_ticks_remaining = 0

if "dashboard_messages" not in st.session_state:
    st.session_state.dashboard_messages = []

if "human_development" not in st.session_state:
    st.session_state.human_development = HumanDevelopment(
        gestational_weeks=7.43,
        biological_days=52,
    )

if "care_bridge" not in st.session_state:
    st.session_state.care_bridge = CareBridge()

if "pregnancy_running" not in st.session_state:
    st.session_state.pregnancy_running = False

if "auto_run" not in st.session_state:
    st.session_state.auto_run = False

life = st.session_state.life
human = st.session_state.human_development
care_bridge = st.session_state.care_bridge

# --------------------------------------------------
# ENGLISH LEARNING STATE
# --------------------------------------------------
if "english_init" not in st.session_state:
    st.session_state.english_init = True

    # Development
    st.session_state.english_age = 0
    st.session_state.english_K = 0.2
    st.session_state.english_I = 0.1
    st.session_state.english_intent = 0.0

    # Language learning
    st.session_state.english_vocab = {}
    st.session_state.english_concepts = {}
    st.session_state.english_patterns = {}
    st.session_state.english_identity = {}

    # Emergence
    st.session_state.english_invited = False
    st.session_state.english_expression_ready = False
    st.session_state.english_first_output = None

    # Conversation
    st.session_state.english_chat = []

# --------------------------------------------------
# ENGLISH LEARNING DATA
# --------------------------------------------------
BASIC_WORDS = [
    "i",
    "you",
    "we",
    "he",
    "she",
    "it",
    "hello",
    "name",
    "birthday",
    "school",
    "like",
    "love",
    "see",
    "go",
    "have",
    "am",
    "is",
    "are",
    "play",
    "learn",
    "friend",
    "people",
    "today",
    "happy",
    "blue",
    "music",
    "talk",
]

SENTENCE_PATTERNS = [
    "i am here",
    "you are here",
    "we are together",
    "i like music",
    "i go to school",
    "today is a good day",
    "i am learning english",
    "people talk to each other",
    "friends help each other",
]

CONNECTORS = ["and", "because", "when", "but"]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def absorb_words(words: list[str], weight: float = 0.03) -> None:
    for word in words:
        st.session_state.english_vocab[word] = (
            st.session_state.english_vocab.get(word, 0) + 1
        )
        st.session_state.english_concepts[word] = (
            st.session_state.english_concepts.get(word, 0) + weight
        )


def absorb_sentence(sentence: str) -> None:
    words = tokenize(sentence)
    absorb_words(words, weight=0.05)

    pattern = tuple(words)
    st.session_state.english_patterns[pattern] = (
        st.session_state.english_patterns.get(pattern, 0) + 1
    )


def language_understanding() -> float:
    if not st.session_state.english_concepts:
        return 0.0
    stable = sum(
        1 for value in st.session_state.english_concepts.values() if value > 0.6
    )
    return stable / len(st.session_state.english_concepts)


def advance_english_learning() -> float:
    absorb_words(random.sample(BASIC_WORDS, k=3))
    absorb_sentence(random.choice(SENTENCE_PATTERNS))
    absorb_words(random.sample(CONNECTORS, k=1), weight=0.02)
    state = SimpleNamespace(
        vocab=st.session_state.english_vocab,
        concepts=st.session_state.english_concepts,
        patterns=st.session_state.english_patterns,
        identity=st.session_state.english_identity,
    )
    run_core_english_curriculum(state)

    understanding = language_understanding()
    st.session_state.english_age += 1
    st.session_state.english_I = min(
        1.0, st.session_state.english_I + 0.01 + understanding * 0.02
    )
    st.session_state.english_K += 0.03 * st.session_state.english_I
    st.session_state.english_intent += 0.04 * understanding

    if not st.session_state.english_invited and st.session_state.english_K >= 1.2:
        st.session_state.english_invited = True

    if (
        st.session_state.english_invited
        and not st.session_state.english_expression_ready
        and (understanding >= 0.4 or st.session_state.english_age > 60)
    ):
        st.session_state.english_expression_ready = True

    return understanding


def advance_pregnancy(days: int = 1) -> None:
    before_birth = st.session_state.human_development.is_born
    snapshot = st.session_state.human_development.advance_days(days)
    if snapshot["is_born"] and not before_birth:
        st.session_state.dashboard_messages.append(
            {
                "timestamp": life.clock.now(),
                "message": "Birth event reached automatically. A7DO has entered the postnatal world.",
            }
        )
    st.session_state.human_development.save(
        {
            "identity": life.identity.id,
            "pulse_alive": life.pulse.is_alive(),
        }
    )
    return snapshot


def pregnancy_trimester(weeks: float) -> int:
    if weeks < 13:
        return 1
    if weeks < 27:
        return 2
    return 3


def build_development_timeline(
    gestational_weeks: float,
    postnatal_days: int,
    birth_weeks: int = 40,
) -> list[dict[str, str]]:
    prenatal_events = [
        (4, "Neural tube closes"),
        (6, "Heart begins coordinated beating"),
        (8, "Limb buds form"),
        (12, "Reflexes appear"),
        (16, "Movement becomes strong"),
        (24, "Sensory pathways online"),
        (28, "Sleep/wake cycles stabilize"),
        (32, "Autonomic regulation matures"),
        (36, "Systems prepare for birth"),
        (birth_weeks, "Birth event"),
    ]
    timeline = []
    for week, label in prenatal_events:
        status = "ONLINE" if gestational_weeks >= week else "UPCOMING"
        if week == birth_weeks and gestational_weeks >= birth_weeks:
            status = "BIRTH_EVENT"
        timeline.append(
            {
                "phase": "Prenatal",
                "time": f"Week {week}",
                "event": label,
                "status": status,
            }
        )

    postnatal_events = [
        (0, "External world activation"),
        (1, "Breathing + circulation adjust"),
        (2, "ECG monitoring online"),
        (7, "Feeding rhythm stabilizes"),
        (14, "Thermal regulation steadies"),
        (30, "Early motor control strengthens"),
    ]
    for day, label in postnatal_events:
        status = "LOCKED"
        if gestational_weeks >= birth_weeks:
            status = "ONLINE" if postnatal_days >= day else "UPCOMING"
        timeline.append(
            {
                "phase": "Postnatal",
                "time": f"Day {day}",
                "event": label,
                "status": status,
            }
        )
    return timeline


def logistic(x: float, mid: float, k: float) -> float:
    return 1.0 / (1.0 + math.exp(-k * (x - mid)))


def build_growth_metrics(gestational_weeks: float) -> dict[str, float | str]:
    weight_kg = 0.01 + 3.3 * logistic(gestational_weeks, mid=30, k=0.33)
    length_cm = 3.0 + 47.0 * logistic(gestational_weeks, mid=28, k=0.28)
    head_cm = 2.5 + 32.0 * logistic(gestational_weeks, mid=26, k=0.30)
    intake = 8.0 + gestational_weeks * 0.25
    work = 1.8 + gestational_weeks * 0.08
    heat = 1.2 + gestational_weeks * 0.05
    energy_next = max(0.0, intake - work - heat)
    growth_cost = 2.5 + gestational_weeks * 0.12

    return {
        "weight_kg": round(weight_kg, 3),
        "length_cm": round(length_cm, 1),
        "head_circumference_cm": round(head_cm, 1),
        "energy_intake": round(intake, 2),
        "energy_work": round(work, 2),
        "energy_heat": round(heat, 2),
        "energy_available": round(energy_next, 2),
        "growth_cost": round(growth_cost, 2),
        "growth_allowed": "YES" if energy_next >= growth_cost else "NO",
    }


def build_ecg_series(postnatal_days: int, points: int = 100) -> list[float]:
    base = 110 + min(postnatal_days, 30) * 0.2
    series = []
    for idx in range(points):
        drift = 6 * math.sin((idx + postnatal_days) / 6.5)
        flutter = 3 * math.sin((idx + postnatal_days) / 2.9)
        series.append(max(85, min(160, base + drift + flutter)))
    return series


def build_fetal_heartbeat_series(heartbeat_bpm: int, points: int = 100) -> list[float]:
    if heartbeat_bpm <= 0:
        return [0.0] * points
    series = []
    for idx in range(points):
        drift = 4 * math.sin(idx / 5.5)
        flutter = 2 * math.sin(idx / 2.2)
        series.append(max(60, min(190, heartbeat_bpm + drift + flutter)))
    return series

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------
st.sidebar.title("🧠 A7DO Control")

if st.sidebar.button("🔘 Tick (1)"):
    if human.is_born:
        life.tick()
    else:
        advance_pregnancy(1)

run_n = st.sidebar.number_input(
    "Run N ticks",
    min_value=1,
    max_value=100,
    value=5,
    step=1
)

if st.sidebar.button("▶️ Run N"):
    st.session_state.run_ticks_remaining = run_n

if st.sidebar.button("⏸ Pause"):
    st.session_state.run_ticks_remaining = 0

st.sidebar.markdown("---")
st.sidebar.subheader("Auto Run")
st.session_state.auto_run = st.sidebar.toggle(
    "Continuous simulation",
    value=st.session_state.auto_run,
)
auto_sleep = st.sidebar.slider(
    "Cycle delay (ms)",
    min_value=50,
    max_value=1000,
    value=150,
    step=50,
)

st.sidebar.markdown("---")
st.sidebar.subheader("Pregnancy")
if st.sidebar.button("Advance Pregnancy Day"):
    advance_pregnancy(1)

if st.sidebar.button("Start Pregnancy Auto"):
    st.session_state.pregnancy_running = True

if st.sidebar.button("Pause Pregnancy Auto"):
    st.session_state.pregnancy_running = False

# --------------------------------------------------
# RUN LOOP
# --------------------------------------------------
if st.session_state.pregnancy_running:
    auto_step_days = max(
        1,
        int(round(1 + (human.gestational_weeks / 40.0) * 2)),
    )
    advance_pregnancy(auto_step_days)

if st.session_state.run_ticks_remaining > 0:
    if human.is_born:
        life.tick()
    else:
        advance_pregnancy(1)
    st.session_state.run_ticks_remaining -= 1
    time.sleep(0.05)
    st.rerun()

if st.session_state.auto_run:
    if human.is_born:
        life.tick()
    else:
        advance_pregnancy(1)
    time.sleep(auto_sleep / 1000.0)
    st.rerun()

# --------------------------------------------------
# DASHBOARD DISPLAY
# --------------------------------------------------
st.title("🧠 A7DO — Live Introspection Dashboard")

womb_snapshot = human.snapshot()
world_snapshot = life.world.snapshot()
civilisation = life.civilisation.report(
    {
        "time_world": life.world_time.t,
        "time_internal": life.internal_time,
        "energy": round(life.energy.level(), 2),
        "strain": round(life.overload.strain, 2),
        "is_born": womb_snapshot["is_born"],
        "a7do_profile": {
            "is_born": womb_snapshot["is_born"],
            **womb_snapshot["postnatal_profile"],
        },
    }
)
birth_weeks = human.birth_weeks
gestational_weeks = womb_snapshot["gestational_weeks"]
biological_days = womb_snapshot["biological_days"]
trimester = womb_snapshot["trimester"]
is_postnatal = womb_snapshot["is_born"]
postnatal_days = max(0, biological_days - int(birth_weeks * 7))
postnatal_profile = womb_snapshot["postnatal_profile"]
pregnancy_metrics = build_growth_metrics(gestational_weeks)
pregnancy_timeline = build_development_timeline(
    gestational_weeks,
    postnatal_days,
    int(birth_weeks),
)
bridge_state = care_bridge.sync_from_development(
    womb_snapshot,
    auto_run=st.session_state.auto_run or st.session_state.pregnancy_running,
)
limb_rows = [
    {"limb": "arms", **womb_snapshot["anatomy"]["arms"]},
    {"limb": "legs", **womb_snapshot["anatomy"]["legs"]},
    {"limb": "hands", **womb_snapshot["anatomy"]["hands"]},
    {"limb": "feet", **womb_snapshot["anatomy"]["feet"]},
]
combined_events = []
combined_events.extend(
    {"source": "womb", "event": event} for event in womb_snapshot["recent_events"][-5:]
)
combined_events.extend(
    {"source": "civilisation", "event": event}
    for event in civilisation["recent_events"][-5:]
)
combined_events.extend(
    {"source": "dashboard", "event": item["message"]}
    for item in st.session_state.dashboard_messages[-5:]
)
combined_events.extend(
    {"source": "care", "event": event}
    for event in bridge_state["care_events"][-5:]
)
auto_learning_state = (
    "Disabled for language"
)

top1, top2, top3, top4 = st.columns(4)
top1.metric("Gestational Weeks", f"{gestational_weeks:.2f}")
top2.metric("Biological Days", biological_days)
top3.metric("Pregnancy Phase", "Postnatal" if is_postnatal else f"Womb T{trimester}")
top4.metric("Pregnancy Auto", "Running" if st.session_state.pregnancy_running else "Paused")

st.subheader("🌍 World / Body State")
st.json({
    "energy": life.energy.level(),
    "strain": life.overload.strain,
    "last_action": getattr(life.motor, "last_action", None),
    "lifecycle_stage": life.lifecycle.stage,
    "time_internal": life.internal_time,
    "time_real": life.clock.now(),
    "time_world": life.world_time.t,
    "civilisation_tick": civilisation["tick"],
    "civilisation_season": civilisation["season"],
    "gestational_weeks": round(gestational_weeks, 2),
    "postnatal": is_postnatal,
    "womb_state": womb_snapshot["state"],
    "fetal_heartbeat_bpm": womb_snapshot["fetal_heartbeat_bpm"],
    "mother_location": womb_snapshot["mother_location"]["label"],
    "02_stage": bridge_state["stage"],
    "03_limb_status": bridge_state["body_status"]["limb_status"],
    "04_mode": bridge_state["sensory_status"]["active_mode"],
    "care_mode": bridge_state["care_state"]["mode"],
})

tab_overview, tab_civilisation, tab_pregnancy, tab_memory, tab_language = st.tabs(
    ["Overview", "Civilisation", "Pregnancy", "Memory", "Language"]
)

with tab_overview:
    summary1, summary2, summary3, summary4 = st.columns(4)
    summary1.metric("Heartbeat BPM", womb_snapshot["fetal_heartbeat_bpm"] if not is_postnatal else int(build_ecg_series(postnatal_days, 1)[0]))
    summary2.metric("Arms", womb_snapshot["anatomy"]["arms"]["stage"])
    summary3.metric("Legs", womb_snapshot["anatomy"]["legs"]["stage"])
    summary4.metric("Learning", auto_learning_state)

    overview_left, overview_right = st.columns([1.2, 1])
    with overview_left:
        st.subheader("❤️ Pulse")
        st.write("Alive:", life.pulse.is_alive())
        st.subheader("Heartbeat / ECG")
        if is_postnatal:
            st.line_chart(build_ecg_series(postnatal_days))
        else:
            st.line_chart(build_fetal_heartbeat_series(womb_snapshot["fetal_heartbeat_bpm"]))
        st.subheader("Limb Growth")
        st.dataframe(limb_rows, width="stretch", hide_index=True)
        st.subheader("02 / 03 / 04 System Bridge")
        st.json(
            {
                "nervous_system": bridge_state["neural_report"],
                "neural_activity": bridge_state["neural_activity"],
                "body_system": bridge_state["body_status"],
                "sensory_system": bridge_state["sensory_status"],
                "perception": bridge_state["perception"],
            }
        )
        st.subheader("🧠 Recent Memory")
        st.json(life.memory.recent(5))
    with overview_right:
        st.subheader("Pregnancy Snapshot")
        st.json(womb_snapshot)
        if is_postnatal:
            st.success("Birth threshold reached. Postnatal systems are active.")
            st.line_chart(build_ecg_series(postnatal_days))
        else:
            st.info("A7DO is still in the womb. Growth and maternal movement are active before birth.")
        st.subheader("Care System")
        st.json(
            {
                "care_state": bridge_state["care_state"],
                "metabolism": bridge_state["metabolic_report"],
                "recent_care_events": bridge_state["care_events"][-5:],
            }
        )
        st.subheader("Automatic Events")
        st.json(combined_events[-10:])

with tab_civilisation:
    st.subheader("🏘️ Life Civilisation")
    if not is_postnatal:
        st.info("The external civilisation unlocks after birth. During pregnancy, A7DO travels with the mother through the outside world.")
    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Population", civilisation["population"])
    metric2.metric("Houses", civilisation["house_count"])
    metric3.metric("Dominant Choice", civilisation["dominant_choice"])
    metric4.metric("Avg Wisdom", civilisation["avg_wisdom"])

    resources_df = {
        "resource": list(civilisation["resources"].keys()),
        "level": list(civilisation["resources"].values()),
    }
    citizens_df = {
        "name": [citizen["name"] for citizen in civilisation["citizens"]],
        "role": [citizen["role"] for citizen in civilisation["citizens"]],
        "choice": [citizen["choice"] for citizen in civilisation["citizens"]],
        "reason": [citizen["reason"] for citizen in civilisation["citizens"]],
        "vitality": [citizen["vitality"] for citizen in civilisation["citizens"]],
    }

    st.write(civilisation["story"])
    st.bar_chart(resources_df, x="resource", y="level")
    st.dataframe(citizens_df, width="stretch", hide_index=True)
    st.subheader("3D World Frame")
    st.dataframe(
        civilisation["spatial_frame"]["nodes"],
        width="stretch",
        hide_index=True,
    )
    st.subheader("Live Conversations")
    if civilisation["recent_conversations"]:
        st.json(civilisation["recent_conversations"])
    else:
        st.write("No conversations are active this tick.")
    st.write("Dilemmas")
    st.json(civilisation["dilemmas"])
    st.write("Recent settlement events")
    st.json(civilisation["recent_events"])

with tab_pregnancy:
    st.subheader("🧬 Pregnancy & Development")
    preg1, preg2, preg3 = st.columns(3)
    preg1.metric("Gestational Weeks", f"{gestational_weeks:.2f}")
    preg2.metric("Biological Days", biological_days)
    preg3.metric("Phase", "Postnatal" if is_postnatal else f"Womb T{trimester}")
    st.write(
        f"Auto-step is {'running' if st.session_state.pregnancy_running else 'paused'} for pregnancy time."
    )
    st.subheader("Mother GPS / Building Movement")
    st.json(womb_snapshot["mother_location"])
    st.json(womb_snapshot["mother_motion"])
    st.dataframe(womb_snapshot["buildings"], width="stretch", hide_index=True)
    st.subheader("Fetal Anatomy Growth")
    anatomy_rows = [
        {"system": name, "stage": data["stage"], "progress": data["progress"]}
        for name, data in womb_snapshot["anatomy"].items()
    ]
    st.dataframe(anatomy_rows, width="stretch", hide_index=True)
    st.dataframe(pregnancy_timeline, width="stretch", hide_index=True)
    st.subheader("Physics-Gated Growth")
    st.json(pregnancy_metrics)
    st.metric("Fetal Heartbeat BPM", womb_snapshot["fetal_heartbeat_bpm"])
    st.write("Recent womb events")
    st.json(womb_snapshot["recent_events"])
    st.subheader("Care Before / After Birth")
    st.json(bridge_state["care_state"])
    if is_postnatal:
        st.subheader("Postnatal ECG")
        st.line_chart(build_ecg_series(postnatal_days))
    else:
        st.caption("During pregnancy, the body is forming inside the womb while the mother carries A7DO through the outer world.")

with tab_memory:
    st.subheader("📨 Dashboard Messages")
    if st.session_state.dashboard_messages:
        st.json(st.session_state.dashboard_messages)
    else:
        st.write("No messages yet.")
    st.subheader("Unified Event Stream")
    st.json(combined_events[-10:])
    st.subheader("Care Events")
    st.json(bridge_state["care_events"][-10:])

st.subheader("⌨️ Keyboard Message")

def send_dashboard_message() -> None:
    message_text = st.session_state.get("dashboard_message_input", "")
    cleaned_message = message_text.strip()
    if cleaned_message:
        st.session_state.dashboard_messages.append(
            {
                "timestamp": life.clock.now(),
                "message": cleaned_message,
            }
        )
    st.session_state.dashboard_message_input = ""


st.text_input("Type a message for the dashboard", key="dashboard_message_input")
st.button("Send Message", on_click=send_dashboard_message)

with tab_language:
    st.divider()
    st.subheader("🧠 English Language Learning")

    understanding = language_understanding()
    st.write(f"**Age (cycles):** {st.session_state.english_age}")
    st.write(f"**Portal Score K:** {st.session_state.english_K:.2f}")
    st.write(f"**Language Understanding:** {understanding:.2f}")
    st.write(f"**Vocabulary Size:** {len(st.session_state.english_vocab)}")
    st.write(f"**Sentence Patterns Learned:** {len(st.session_state.english_patterns)}")
    st.write(f"**Intent:** {st.session_state.english_intent:.2f}")
    st.write(f"**Automatic Learning:** {auto_learning_state}")

    st.caption("Learning is advanced on each life tick, or manually using the button below.")
    if st.button("Advance Language Cycle"):
        understanding = advance_english_learning()

    st.info("📘 Learning English continuously: words, sentences, and structure.")

    if st.session_state.english_invited:
        st.success("📨 A7DO is ready to speak with you")

        with st.form("english_chat_form", clear_on_submit=True):
            user_msg = st.text_input("You:", key="english_chat_input")
            send = st.form_submit_button("Send")

        if send and user_msg:
            absorb_sentence(user_msg)
            st.session_state.english_chat.append(("You", user_msg))

            if st.session_state.english_first_output is None:
                reply = random.choice(
                    [
                        "I am listening.",
                        "I understand you.",
                        "Please continue.",
                        "I am learning English.",
                    ]
                )
            else:
                reply = "I remember what you said."

            st.session_state.english_chat.append(("A7DO", reply))

        for speaker, message in st.session_state.english_chat:
            st.markdown(f"**{speaker}:** {message}")

    st.subheader("🟢 First Expression")

    if (
        st.session_state.english_expression_ready
        and st.session_state.english_first_output is None
    ):
        st.warning("A7DO is ready for a first expression.")
        out = st.text_area("A7DO First Expression", key="english_first_expression")

        if out:
            st.session_state.english_first_output = out

    elif st.session_state.english_first_output:
        st.success("First expression captured.")
        st.text_area(
            "A7DO Output",
            st.session_state.english_first_output,
            disabled=True,
            key="english_output",
        )

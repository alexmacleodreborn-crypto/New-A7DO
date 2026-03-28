import streamlit as st
import pandas as pd
import time
import random
import os
import sys
from datetime import datetime, timedelta

# --- PATH CORRECTION LOGIC ---
# This ensures Python can see inside your 00, 02, 03, 04, and 09 folders
def add_folders_to_path():
    root = os.getcwd()
    folders = [
        "00_CORE_EXISTENCE",
        "02_NERVOUS_SYSTEM",
        "03_BODY_SYSTEM",
        "04_SENSORY_SYSTEM",
        "09_WORLD_MODEL"
    ]
    for f in folders:
        path = os.path.join(root, f)
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)

add_folders_to_path()

# --- ROBUST IMPORTS ---
# Using the exact names you confirmed in our conversation
try:
    from core_existence import A7DO_Core
    from nervous_system import A7DO_NervousSystem
    from body import A7DO_Body
    from a7do_sensory import A7DO_Sensory
    from metabolism_master import A7DO_Metabolism
    from limbic_master import A7DO_Limbic
    from a7do_memory_master import A7DO_Memory
    from world_model_master import EarthKinWorld
except ImportError as e:
    st.error(f"⚠️ Import Error: {e}")
    st.info("Ensure all master files (metabolism_master.py, etc.) are in the root or their respective folders.")
    st.stop()

# --- DASHBOARD CONFIG ---
st.set_page_config(page_title="A7DO Life Observer", layout="wide")

# Initialize Session State
if 'initialized' not in st.session_state:
    try:
        st.session_state.world = EarthKinWorld()
        st.session_state.core = A7DO_Core()
        st.session_state.ns = A7DO_NervousSystem(st.session_state.core)
        st.session_state.body = A7DO_Body(st.session_state.core)
        st.session_state.sensory = A7DO_Sensory(st.session_state.core)
        st.session_state.metabolism = A7DO_Metabolism(st.session_state.core)
        st.session_state.limbic = A7DO_Limbic(st.session_state.core, st.session_state.metabolism)
        st.session_state.memory = A7DO_Memory(st.session_state.core)
        st.session_state.logs = ["System Initialized: Subjective Time Active."]
        st.session_state.initialized = True
    except Exception as e:
        st.error(f"Initialization Failed: {e}")
        st.stop()

def run_life_tick():
    """Syncs Earth-Kin world time with A7DO's internal pulse."""
    # 1. World advances (600 seconds = 10 minutes per tick)
    world_tick = st.session_state.world.update_world_tick(600)
    
    # 2. A7DO perceives the tick
    pulse_data = st.session_state.core.process_pulse(600)
    event = st.session_state.core.update_growth()
    if event: st.session_state.logs.append(f"Growth Event: {event}")

    # 3. Biology & Perception
    st.session_state.body.update_physical_growth()
    st.session_state.metabolism.update_metabolic_state(world_tick['temp'])
    
    # 4. Perception
    perceived = st.session_state.sensory.process_external_stimuli({
        "is_day": world_tick['is_day'],
        "light_intensity": 80 if world_tick['is_day'] else 5,
        "village_sounds": random.randint(20, 70),
        "temperature": world_tick['temp']
    })
    
    # 5. Choice
    st.session_state.limbic.update_emotional_loop(perceived)
    choice = st.session_state.limbic.make_behavioral_choice()
    st.session_state.memory.store_in_stm(perceived, st.session_state.limbic.emotions)
    
    return perceived, choice

# --- UI LAYOUT ---
st.title("🧬 A7DO Life Observer")
st.caption(f"Identity: {st.session_state.core.identity['uid']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Internal Stage", st.session_state.core.current_stage)
with col2:
    st.metric("World Time", st.session_state.world.get_world_summary()['village_clock'])
with col3:
    st.metric("Metabolic Energy", st.session_state.metabolism.get_metabolic_report()['energy'])

# Control Center
if st.button("Manual Life Pulse 💓"):
    run_life_tick()

tab1, tab2, tab3 = st.tabs(["🌎 World View", "🧠 Neural/Limbic", "📈 Biology"])

with tab1:
    st.subheader("Earth-Kin Village")
    world_data = st.session_state.world.get_world_summary()
    st.write(f"Current Weather: {world_data['weather']}")
    st.write(f"Active Citizens: {world_data['tier2_active']}")
    
with tab2:
    st.subheader("Emotional & Memory State")
    limbic_rep = st.session_state.limbic.get_limbic_report()
    st.write(f"Dominant Emotion: {limbic_rep['mood']}")
    st.write(f"Active Choice: **{limbic_rep['current_choice']}**")
    st.json(st.session_state.memory.get_memory_report())

with tab3:
    st.subheader("Anatomical Growth")
    st.json(st.session_state.body.get_physical_status())

# Event Log
st.markdown("---")
st.write("### Subjective Event Log")
for log in reversed(st.session_state.logs[-10:]):
    st.text(f"> {log}")


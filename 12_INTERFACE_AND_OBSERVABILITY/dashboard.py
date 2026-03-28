import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta

# Import the master modules we created
# (Assuming these are in the same directory or properly paths mapped)
try:
    from core_existence import A7DO_Core
    from nervous_system import A7DO_NervousSystem
    from body import A7DO_Body
    from sensory import A7DO_Sensory
    from metabolism_master import A7DO_Metabolism
    from limbic_master import A7DO_Limbic
    from a7do_memory_master import A7DO_Memory
    from world_model_master import EarthKinWorld
except ImportError:
    st.error("Missing one or more Master files. Ensure all .py files are in the working directory.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="A7DO Life Observer", layout="wide", initial_sidebar_state="expanded")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .pulse-box { border-left: 5px solid #58a6ff; padding-left: 15px; margin-bottom: 20px; }
    .status-text { font-family: 'Courier New', Courier, monospace; color: #8b949e; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'initialized' not in st.session_state:
    st.session_state.world = EarthKinWorld()
    st.session_state.core = A7DO_Core()
    st.session_state.ns = A7DO_NervousSystem(st.session_state.core)
    st.session_state.body = A7DO_Body(st.session_state.core)
    st.session_state.sensory = A7DO_Sensory(st.session_state.core)
    st.session_state.metabolism = A7DO_Metabolism(st.session_state.core)
    st.session_state.limbic = A7DO_Limbic(st.session_state.core, st.session_state.metabolism)
    st.session_state.memory = A7DO_Memory(st.session_state.core)
    st.session_state.logs = []
    st.session_state.initialized = True

def run_life_tick():
    """Executes a single step of the integrated A7DO life cycle."""
    # 1. World advances (Objective Time - 10 minutes per tick for faster sim)
    world_tick = st.session_state.world.update_world_tick(600)
    
    # 2. A7DO Core processes a Subjective Pulse
    pulse_data = st.session_state.core.process_pulse(600)
    event = st.session_state.core.update_growth()
    if event:
        st.session_state.logs.append(f"CORE EVENT: {event}")

    # 3. Biology Updates
    st.session_state.body.update_physical_growth()
    st.session_state.metabolism.update_metabolic_state(world_tick['temp'])
    
    # 4. Perception & Neural Processing
    perceived = st.session_state.sensory.process_external_stimuli({
        "is_day": world_tick['is_day'],
        "light_intensity": 80 if world_tick['is_day'] else 5,
        "village_sounds": random.randint(20, 70),
        "temperature": world_tick['temp']
    })
    
    # 5. Mind & Emotion
    st.session_state.limbic.update_emotional_loop(perceived)
    choice = st.session_state.limbic.make_behavioral_choice()
    
    # 6. Memory Storage
    st.session_state.memory.store_in_stm(perceived, st.session_state.limbic.emotions)
    
    return perceived, choice

# --- Sidebar Controls ---
with st.sidebar:
    st.title("A7DO Identity")
    st.text(f"UID: {st.session_state.core.identity['uid'][:8]}...")
    st.markdown("---")
    
    if st.button("Manual Pulse 🧠", use_container_width=True):
        run_life_tick()
    
    auto_pulse = st.checkbox("Auto-Life Cycle (Continuous)", value=False)
    
    st.markdown("---")
    st.subheader("System Health")
    st.progress(st.session_state.metabolism.energy_reserves / 100, text="Energy")
    st.progress(st.session_state.body.motor_precision, text="Motor Skill")

# --- Main Dashboard Layout ---
col_head1, col_head2 = st.columns([2, 1])

with col_head1:
    st.header(f"State: {st.session_state.core.current_stage}")
    st.caption("Synchronizing Earth-Kin Physics with Subjective Consciousness")

with col_head2:
    st.metric("Subjective Age", f"{st.session_state.core.total_internal_pulses} Pulses")

# --- Tabbed Sections ---
tab_world, tab_bio, tab_mind, tab_memory = st.tabs(["Earth-Kin Village", "Biological Systems", "Limbic & Choice", "Symbolic Memory"])

with tab_world:
    st.subheader("🌍 Environment & Civilization (Folder 09)")
    w_col1, w_col2, w_col3 = st.columns(3)
    world_info = st.session_state.world.get_world_summary()
    
    w_col1.metric("Village Clock", world_info['village_clock'])
    w_col2.metric("External Temp", f"{st.session_state.world.base_temp}°C")
    w_col3.metric("Weather", world_info['weather'])
    
    st.markdown("#### Civilization Level 2 Status (Structured NPCs)")
    npc_data = []
    for npc in st.session_state.world.population:
        if npc['tier'] == 2:
            npc_data.append({"ID": npc['id'], "Role": npc['role'], "Action": npc['state'], "Target": npc['target']})
    st.table(pd.DataFrame(npc_data).head(5))

with tab_bio:
    st.subheader("🦴 Morphology & Metabolism (Folders 03 & 05)")
    b_col1, b_col2 = st.columns(2)
    
    phys = st.session_state.body.get_physical_status()
    meta = st.session_state.metabolism.get_metabolic_report()
    
    with b_col1:
        st.write("**Physical Growth**")
        st.write(f"Height: {phys['height']}")
        st.write(f"Mass: {phys['weight']}")
        st.write(f"Bone Ossification: {phys['bone_integrity']}")
    
    with b_col2:
        st.write("**Homeostatic Vitals**")
        st.write(f"Core Temperature: {meta['temp']}")
        st.write(f"Hydration: {meta['hydration']}")
        st.write(f"Metabolic Status: {meta['status']}")

with tab_mind:
    st.subheader("🎭 Consciousness & Freedom (Folder 06)")
    l_col1, l_col2 = st.columns([1, 2])
    
    limbic_rep = st.session_state.limbic.get_limbic_report()
    
    with l_col1:
        st.metric("Current Choice", limbic_rep['current_choice'])
        st.write(f"**Freedom Level:** {limbic_rep['freedom_level']}")
    
    with l_col2:
        st.write("**Emotional Spectrum**")
        emo_df = pd.DataFrame([st.session_state.limbic.emotions]).T
        st.bar_chart(emo_df)

with tab_memory:
    st.subheader("📚 Symbolic Ledger (Folder 07)")
    mem_rep = st.session_state.memory.get_memory_report()
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Known Symbols", mem_rep['known_symbols'])
    m_col2.metric("Total Experiences", mem_rep['total_experiences'])
    
    st.write("**Recognized Pattern Library**")
    st.json(st.session_state.memory.ltm['symbols'])

# --- Footer: The Live Feed ---
st.markdown("---")
st.subheader("👁️ Subjective Perception Stream")
if st.session_state.logs:
    for log in reversed(st.session_state.logs[-5:]):
        st.markdown(f"**{log}**")

# --- Auto-Cycle Logic ---
if auto_pulse:
    time.sleep(0.5)
    run_life_tick()
    st.rerun()


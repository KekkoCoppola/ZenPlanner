import streamlit as st
import pandas as pd
import sys
import os
import streamlit.components.v1 as components

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.csp_scheduler.domain import UserProfile, TimeSlot, StudySession
from src.csp_scheduler.scheduler import ZenSchedulerEngine

st.set_page_config(page_title="ZenPlanner AI", page_icon="🧘", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Poppins:wght@300;400;500;600;700&display=swap');

/* ── BASE ── */
html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }
h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; letter-spacing: -0.5px; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }

.stApp {
    background: radial-gradient(ellipse at 10% 0%, #1a1a2e 0%, #16213e 45%, #0f3460 100%);
    min-height: 100vh;
}

/* Scroll padding for navbar */
.block-container {
    padding: 2rem 3rem 110px 3rem !important;
    max-width: 1400px !important;
}

/* ── ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { left: -100%; }
    20%  { left: 200%; }
    100% { left: 200%; }
}
@keyframes glowPulse {
    0%,100% { box-shadow: 0 0 20px rgba(0,180,216,0.15); }
    50%      { box-shadow: 0 0 35px rgba(0,180,216,0.35); }
}

/* ── GLASS CARDS ── */
.glass-card {
    background: rgba(15, 22, 50, 0.6);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 32px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 28px;
    animation: fadeUp 0.5s ease-out forwards;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0,180,216,0.3);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
}
.glass-card h3 {
    color: #00E5FF;
    margin-top: 0;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    opacity: 0.85;
    margin-bottom: 6px;
}
.glass-card p.big-value {
    font-family: 'Outfit', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    color: #FFF;
    margin: 8px 0 0 0;
    text-shadow: 0 0 20px rgba(0,229,255,0.5);
    line-height: 1;
}
.glass-card p.big-value.danger { color: #ff6b6b; text-shadow: 0 0 20px rgba(255,71,87,0.4); }
.glass-card p.big-value.warn   { color: #ffd166; text-shadow: 0 0 20px rgba(255,185,0,0.4); }
.glass-card p.big-value.safe   { color: #a8dadc; text-shadow: 0 0 20px rgba(0,229,255,0.4); }

/* ── STRESS BADGE ── */
.stress-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-top: 10px;
    letter-spacing: 0.5px;
}
.stress-badge.danger { background: rgba(255,71,87,0.2); color: #ff6b6b; border: 1px solid rgba(255,71,87,0.4); }
.stress-badge.warn   { background: rgba(255,185,0,0.2);  color: #ffd166; border: 1px solid rgba(255,185,0,0.4); }
.stress-badge.safe   { background: rgba(0,200,150,0.2);  color: #a8dadc; border: 1px solid rgba(0,200,150,0.4); }

/* ── SCHEDULE CARDS ── */
.schedule-header {
    text-align: center;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    color: #FF9F1C;
    padding: 8px 0 10px;
    border-bottom: 2px solid rgba(255,159,28,0.25);
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.schedule-card {
    background: linear-gradient(135deg, #4ea8de, #6930c3);
    color: #fff;
    padding: 10px 8px;
    border-radius: 12px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 8px;
    font-size: 0.82rem;
    box-shadow: 0 4px 12px rgba(105,48,195,0.35);
    border: 1px solid rgba(255,255,255,0.15);
    animation: fadeUp 0.4s ease-out forwards;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
    line-height: 1.3;
}
.schedule-card::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 50%; height: 100%;
    background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.25) 50%, rgba(255,255,255,0) 100%);
    transform: skewX(-25deg);
    animation: shimmer 3.5s infinite;
}
.schedule-card:hover { transform: scale(1.04) translateY(-2px); box-shadow: 0 8px 20px rgba(105,48,195,0.55); }
.empty-slot {
    background: rgba(255,255,255,0.03);
    border: 1px dashed rgba(255,255,255,0.1);
    padding: 8px;
    border-radius: 12px;
    margin-bottom: 8px;
    height: 58px;
    transition: background 0.2s;
}
.empty-slot:hover { background: rgba(255,255,255,0.06); }

/* ── FORM ── */
[data-testid="stForm"] {
    background: rgba(15,22,50,0.55);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 32px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    animation: glowPulse 4s ease-in-out infinite;
}

/* ── INPUTS ── */
[data-testid="stNumberInput"] > div > div > input,
[data-testid="stTextInput"] > div > div > input {
    background: rgba(0,0,0,0.35) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-family: 'Poppins', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stNumberInput"] > div > div > input:focus,
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #00B4D8 !important;
    box-shadow: 0 0 0 3px rgba(0,180,216,0.18) !important;
    outline: none !important;
}
[data-testid="stNumberInput"] button {
    background: rgba(0,180,216,0.12) !important;
    border: 1px solid rgba(0,180,216,0.25) !important;
    color: #00B4D8 !important;
    border-radius: 8px !important;
    transition: background 0.2s !important;
}
[data-testid="stNumberInput"] button:hover { background: rgba(0,180,216,0.28) !important; }

[data-testid="stSelectbox"] > div > div {
    background: rgba(0,0,0,0.35) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}
[data-testid="stMultiSelect"] > div > div {
    background: rgba(0,0,0,0.35) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: rgba(14, 22, 52, 0.75) !important;
    backdrop-filter: blur(8px) !important;
    color: #C8D6E5 !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.8rem !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    background: rgba(114,9,183,0.55) !important;
    border-color: #00B4D8 !important;
    box-shadow: 0 6px 18px rgba(114,9,183,0.4) !important;
    color: #fff !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(0,180,216,0.7), rgba(114,9,183,0.7)) !important;
    border-color: rgba(0,180,216,0.5) !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(0,180,216,0.9), rgba(114,9,183,0.9)) !important;
    box-shadow: 0 8px 24px rgba(0,180,216,0.35) !important;
}

/* ── INSIGHT BANNER ── */
.insight-block {
    background: rgba(255,159,28,0.12);
    border-left: 4px solid #FF9F1C;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
    font-size: 0.9rem;
    line-height: 1.6;
    color: #ffe0b2;
    animation: fadeUp 0.5s ease-out;
}

/* ── SECTION DIVIDER ── */
.section-label {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.4);
    margin: 24px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

/* ── PAGE HEADER ── */
.page-header {
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.page-header h1 {
    font-size: 2rem !important;
    margin-bottom: 4px !important;
    background: linear-gradient(135deg, #fff 0%, #a8d8ea 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-header p { color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 0; }

/* ── SUBJECT QUEUE ITEM ── */
.subj-item {
    display: flex; align-items: center; gap: 12px;
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.subj-item:hover { border-color: rgba(0,180,216,0.3); }
.subj-dot { width: 8px; height: 8px; border-radius: 50%; background: #00E5FF; flex-shrink: 0; box-shadow: 0 0 6px rgba(0,229,255,0.6); }
.subj-name { flex: 1; font-weight: 600; font-size: 0.92rem; }
.subj-hours { color: #00B4D8; font-weight: 700; font-size: 0.85rem; }
.subj-dead { color: #FF9F1C; font-size: 0.78rem; }

/* ── NAVBAR (hidden — replaced by top bar via JS) ── */
.nav-marker { display: none !important; }

/* ── RADIO ── */
[data-testid="stRadio"] > div { gap: 8px !important; }
[data-testid="stRadio"] label {
    background: rgba(0,0,0,0.25) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 6px 18px !important;
    transition: all 0.2s !important;
}
[data-testid="stRadio"] label:hover { border-color: rgba(0,180,216,0.4) !important; }

/* ── INFO/SUCCESS/ERROR ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
    font-size: 0.88rem !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(0,180,216,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,180,216,0.5); }
</style>
""", unsafe_allow_html=True)

# ─── STATE ──────────────────────────────────────────────────────────────────────
logo_path = os.path.join(base_dir, "assets", "ZenPlannerLogo.png")

for key, default in [
    ('logged_in', False), ('user_name', ''), ('stress_level', None),
    ('study_plan', {}), ('profile_configured', False), ('user_profile', None),
    ('engine_msg', ''), ('subjects_list', [])
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─── PAGES ──────────────────────────────────────────────────────────────────────
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:28px;'>
          <h1 style='font-family:Outfit,sans-serif; font-weight:800; font-size:2.2rem;
                     background:linear-gradient(135deg,#fff 0%,#a8d8ea 100%);
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                     background-clip:text; margin:0 0 8px;'>Benvenuto in ZenPlanner</h1>
          <p style='color:rgba(255,255,255,0.45); font-size:0.9rem; margin:0;'>
            Intelligenza Artificiale per il tuo Benessere Accademico
          </p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=True):
            name = st.text_input("Il tuo Nome", placeholder="Es. Marco Rossi")
            if st.form_submit_button("Accedi al Sistema →", use_container_width=True, type="primary") and name:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = name
                st.rerun()


def view_profile():
    st.markdown("""
    <div class='page-header'>
      <h1>Profilo Utente</h1>
      <p>Configura le tue abitudini per calibrare il piano di studio personalizzato.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("<div class='section-label'>🎓 Dati Accademici & Fisici</div>", unsafe_allow_html=True)
        age   = st.number_input("Età", min_value=18, max_value=80, value=22, step=1)
        sleep = st.number_input("Ore di Sonno / notte", min_value=3.0, max_value=14.0, value=7.0, step=0.5)
        study = st.number_input("Carico Studio Attuale (h/settimana)", min_value=0, max_value=80, value=20, step=1)
        gpa   = st.number_input("Rendimento Accademico GPA (0–4)", min_value=0.0, max_value=4.0, value=3.0, step=0.1)
    with c2:
        st.markdown("<div class='section-label'>📱 Routine e Sfide</div>", unsafe_allow_html=True)
        social           = st.number_input("Social Media (h/giorno)", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
        exercise         = st.number_input("Attività Fisica (h/settimana)", min_value=0, max_value=40, value=3, step=1)
        family_support   = st.number_input("Supporto Familiare (1–5)", min_value=1, max_value=5, value=3, step=1)
        financial_stress = st.number_input("Stress Finanziario (1–5)", min_value=1, max_value=5, value=3, step=1)
    with c3:
        st.markdown("<div class='section-label'>🧠 Pressioni Psicologiche</div>", unsafe_allow_html=True)
        peer_pressure  = st.number_input("Pressione Sociale (1–5)", min_value=1, max_value=5, value=3, step=1)
        relation_stress= st.number_input("Stress Relazionale (1–5)", min_value=1, max_value=5, value=2, step=1)
        diet_quality   = st.number_input("Qualità Dieta (1–5)", min_value=1, max_value=5, value=3, step=1)

    st.markdown("<div class='section-label'>🌿 Strategie di Coping dello Stress</div>", unsafe_allow_html=True)
    coping_options = [
        "Esercizio", "Meditazione", "Lettura", "Social Media",
        "Passare Il Tempo In Solitaria", "Parlare con gli amici", "Viaggiare",
        "Passeggiare", "Guardare Sport", "Yoga"
    ]
    selected_coping = st.multiselect(
        "Seleziona le attività che svolgi abitualmente:",
        options=coping_options, default=[]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salva Profilo", use_container_width=True, type="primary"):
        coping_dict = {f"Coping_{opt}": (1 if opt in selected_coping else 0) for opt in coping_options}
        st.session_state['user_profile'] = UserProfile(
            age=age, gpa=gpa, social_media_hours_per_day=social, sleep_hours_per_night=sleep,
            physical_exercise_hours_per_week=exercise, family_support=family_support,
            financial_stress=financial_stress, peer_pressure=peer_pressure,
            relationship_stress=relation_stress, diet_quality=diet_quality,
            coping_mechanisms=coping_dict
        )
        st.session_state['profile_configured'] = True
        st.success("✅ Profilo salvato! Vai al Planner per generare il tuo piano.")


def view_scheduler():
    st.markdown("""
    <div class='page-header'>
      <h1>Generatore Piano Settimanale 🚀</h1>
      <p>Inserisci le materie da studiare e lascia che l'AI trovi la distribuzione ottimale.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state['profile_configured']:
        st.error("⚠️ Configura prima il tuo **Profilo Utente** e premi Salva!")
        return

    user = st.session_state.get('user_profile')
    if user is None:
        st.error("Il profilo è obsoleto. Torna in Profilo e premi Salva!")
        return

    st.markdown("<div class='section-label'>📚 Aggiungi Materia</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 1.5, 2, 1])
    with c1: subj_name = st.text_input("Titolo / Materia", placeholder="Es. Analisi I, Machine Learning…")
    with c2: subj_hours = st.number_input("Ore necessarie", 1, 40, 5)
    with c3: subj_dead = st.selectbox("Scadenza limite", ["Nessuna","Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"])
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Aggiungi"):
            if subj_name:
                st.session_state['subjects_list'].append({"name": subj_name, "hours": subj_hours, "deadline": subj_dead})
                st.rerun()

    if st.session_state['subjects_list']:
        st.markdown("<div class='section-label'>📋 Coda di Elaborazione</div>", unsafe_allow_html=True)
        for s in st.session_state['subjects_list']:
            deadline_text = f"⏳ Entro {s['deadline']}" if s['deadline'] != 'Nessuna' else ''
            st.markdown(f"""
            <div class='subj-item'>
              <div class='subj-dot'></div>
              <span class='subj-name'>{s['name']}</span>
              <span class='subj-hours'>{s['hours']}h</span>
              <span class='subj-dead'>{deadline_text}</span>
            </div>""", unsafe_allow_html=True)

        ca, cb = st.columns([4, 1])
        with cb:
            if st.button("🗑 Pulisci lista"):
                st.session_state['subjects_list'] = []
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Avvia Generazione Piano di Studio", use_container_width=True, type="primary"):
        if not st.session_state['subjects_list']:
            st.warning("Inserisci almeno una materia!")
            return

        engine = ZenSchedulerEngine(user)
        slots = [TimeSlot(day_of_week=d, start_time=h) for d in range(7) for h in range(9, 18)]
        planned_sessions = []
        days_map = {"Lunedì":0,"Martedì":1,"Mercoledì":2,"Giovedì":3,"Venerdì":4,"Sabato":5,"Domenica":6}
        for s in st.session_state['subjects_list']:
            dd = days_map.get(s['deadline'], None)
            for i in range(s['hours']):
                planned_sessions.append(StudySession(id=f"{s['name']}_hw{i+1}", subject=s['name'], deadline_day=dd))

        with st.spinner("L'Engine CSP è in esplorazione dell'albero di ricerca…"):
            assignment, insight_msg = engine.generate_schedule(planned_sessions, slots)

        total_hours = sum(s['hours'] for s in st.session_state['subjects_list'])
        st.session_state['stress_level'] = engine.predict_baseline_stress(total_hours)
        st.session_state['engine_msg'] = insight_msg

        days = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
        plan = {day: {h: None for h in range(9, 18)} for day in days}
        if assignment:
            for session, slot in assignment.items():
                day_name = days[slot.day_of_week]
                plan[day_name][slot.start_time] = f"{slot.start_time:02d}:00–{slot.start_time+1:02d}:00<br><b>{session.subject}</b>"
            st.session_state['study_plan'] = plan
            st.success("✅ Piano generato! Visualizzalo nella Dashboard.")
        else:
            st.error("❌ Impossibile trovare una soluzione. Riduci il carico o allenta le scadenze.")
            st.session_state['study_plan'] = {}


def view_dashboard():
    st.markdown("""
    <div class='page-header'>
      <h1>Analytics & Dashboard 📊</h1>
      <p>Panoramica del piano di studio generato dall'AI e predizione del rischio burnout.</p>
    </div>
    """, unsafe_allow_html=True)

    stress = st.session_state.get('stress_level')

    if stress is None:
        # Empty state — guide the user
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; opacity:0.6;'>
          <div style='font-size:3rem; margin-bottom:16px;'>🧘</div>
          <h3 style='font-family:Outfit,sans-serif; font-weight:700; color:rgba(255,255,255,0.7); margin-bottom:8px;'>
            Nessun piano ancora generato
          </h3>
          <p style='font-size:0.9rem; color:rgba(255,255,255,0.4);'>
            Vai su <strong>Profilo</strong> per configurare i tuoi dati, poi usa il <strong>Planner</strong> per generare il piano.
          </p>
        </div>
        """, unsafe_allow_html=True)
        return

    s_text = f"{stress:.2f}"
    stress_class = "danger" if stress > 7 else ("warn" if stress > 5 else "safe")
    stress_label = "🔴 Rischio Burnout Elevato" if stress > 7 else ("🟡 Carico Moderato" if stress > 5 else "🟢 Carico Sostenibile")

    total_blocks = sum(sum(1 for v in ds.values() if v is not None) for ds in st.session_state.get('study_plan', {}).values())

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;'>
          <h3>Predizione Stress Burnout</h3>
          <p class='big-value {stress_class}'>{s_text}<span style='font-size:1.2rem;opacity:0.5;'>/10</span></p>
          <span class='stress-badge {stress_class}'>{stress_label}</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;'>
          <h3>Blocchi (1h) Allocati</h3>
          <p class='big-value'>{total_blocks}<span style='font-size:1.2rem;opacity:0.5;'> slot</span></p>
          <span class='stress-badge safe'>Piano settimanale attivo</span>
        </div>""", unsafe_allow_html=True)

    engine_msg = st.session_state.get('engine_msg')
    if engine_msg:
        st.markdown(f"<div class='insight-block'>🧠 <strong>Insight ML:</strong> {engine_msg}</div>", unsafe_allow_html=True)

    plan = st.session_state.get('study_plan', {})
    if not plan:
        st.info("Piano non ancora generato.")
        return

    view_type = st.radio("Vista calendario", ["Visualizzazione Settimanale", "Focus Giornaliero"], horizontal=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if view_type == "Visualizzazione Settimanale":
        cols = st.columns(7)
        for idx, (day, day_slots) in enumerate(plan.items()):
            with cols[idx]:
                st.markdown(f"<div class='schedule-header'>{day[:3]}</div>", unsafe_allow_html=True)
                for h in range(9, 18):
                    s = day_slots[h]
                    if s:
                        st.markdown(f"<div class='schedule-card'>{s}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='empty-slot'></div>", unsafe_allow_html=True)
    else:
        c_sel, _ = st.columns([1, 2])
        with c_sel:
            day_selected = st.selectbox("Seleziona Giorno", list(plan.keys()))
        st.markdown(f"<h2 style='text-align:center; color:#FF9F1C; font-family:Outfit,sans-serif;'>{day_selected}</h2>", unsafe_allow_html=True)
        day_slots = plan[day_selected]
        if not any(v is not None for v in day_slots.values()):
            st.markdown("<div style='text-align:center; opacity:0.5; padding:40px;'>🌿 Zen mode — nessuna sessione programmata</div>", unsafe_allow_html=True)
        else:
            for h in range(9, 18):
                s = day_slots[h]
                if s:
                    st.markdown(f"<div class='schedule-card' style='max-width:420px; margin:10px auto; padding:18px;'>{s}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='empty-slot' style='max-width:420px; margin:10px auto;'></div>", unsafe_allow_html=True)


# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state['logged_in']:
        login_page()
        return

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'dashboard'

    page = st.session_state['current_page']
    if page == "dashboard":   view_dashboard()
    elif page == "profile":   view_profile()
    elif page == "scheduler": view_scheduler()
    else:                     view_dashboard()

    # ── Top navbar via JS injection ──
    with st.container(border=True):
        st.markdown('<div class="nav-marker"></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            t = "primary" if page == "dashboard" else "secondary"
            if st.button("🏠 Dashboard", key="go_dash", use_container_width=True, type=t):
                st.session_state['current_page'] = 'dashboard'; st.rerun()
        with c2:
            t = "primary" if page == "profile" else "secondary"
            if st.button("👤 Profilo", key="go_prof", use_container_width=True, type=t):
                st.session_state['current_page'] = 'profile'; st.rerun()
        with c3:
            t = "primary" if page == "scheduler" else "secondary"
            if st.button("📅 Planner", key="go_sched", use_container_width=True, type=t):
                st.session_state['current_page'] = 'scheduler'; st.rerun()

    # JavaScript: move navbar to top as a floating header bar (desktop-first design)
    components.html("""
    <script>
    function fixNavbar() {
        var markers = window.parent.document.querySelectorAll('.nav-marker');
        if (markers.length === 0) return;
        var m = markers[0];
        var container = m.closest('[data-testid="stVerticalBlockBorderWrapper"]')
                     || m.closest('[data-testid="stVerticalBlock"]');
        if (!container) return;

        container.style.cssText = `
            position: fixed !important;
            top: 0px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: 1400px !important;
            background: rgba(8, 14, 38, 0.90) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 0 !important;
            padding: 10px 32px !important;
            z-index: 999999 !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.5) !important;
            display: flex !important;
            align-items: center !important;
        `;

        // Style the inner column container to be horizontal
        var colWrap = container.querySelector('[data-testid="stHorizontalBlock"]');
        if (colWrap) {
            colWrap.style.cssText = 'display:flex; align-items:center; gap:8px; width:100%;';
        }

        var btns = container.querySelectorAll('button');
        btns.forEach(function(btn) {
            var isPrimary = btn.getAttribute('kind') === 'primary'
                         || !!btn.closest('[data-testid="baseButton-primary"]');

            btn.style.cssText = `
                background: ${isPrimary ? 'rgba(0,180,216,0.18)' : 'transparent'} !important;
                border: ${isPrimary ? '1px solid rgba(0,180,216,0.4)' : '1px solid transparent'} !important;
                color: ${isPrimary ? '#00E5FF' : 'rgba(255,255,255,0.5)'} !important;
                font-family: Outfit, sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.85rem !important;
                padding: 7px 20px !important;
                border-radius: 10px !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                white-space: nowrap !important;
                min-height: 0 !important;
            `;

            btn.addEventListener('mouseenter', function() {
                if (!isPrimary) {
                    btn.style.background = 'rgba(255,255,255,0.06)';
                    btn.style.color = 'rgba(255,255,255,0.85)';
                }
            });
            btn.addEventListener('mouseleave', function() {
                if (!isPrimary) {
                    btn.style.background = 'transparent';
                    btn.style.color = 'rgba(255,255,255,0.5)';
                }
            });

            var inner = btn.querySelectorAll('p, div, span');
            inner.forEach(function(el) {
                el.style.cssText = 'white-space:nowrap !important; overflow:visible !important; text-overflow:unset !important; font-size:inherit !important;';
            });
        });

        // Add logo text on the left
        var existing = container.querySelector('.zen-logo-text');
        if (!existing) {
            var logo = document.createElement('div');
            logo.className = 'zen-logo-text';
            logo.style.cssText = 'font-family:Outfit,sans-serif; font-weight:800; font-size:1rem; color:#00E5FF; letter-spacing:1px; margin-right:auto; flex-shrink:0; padding-right:16px;';
            logo.innerHTML = '🧘 ZENPLANNER AI';
            container.insertBefore(logo, container.firstChild);
        }
    }

    // Adjust block-container top padding to account for navbar height
    function adjustPadding() {
        var bc = window.parent.document.querySelector('.block-container');
        if (bc) bc.style.paddingTop = '72px';
    }

    setTimeout(fixNavbar, 150);
    setTimeout(fixNavbar, 400);
    setTimeout(fixNavbar, 900);
    setTimeout(adjustPadding, 200);
    new MutationObserver(function() { fixNavbar(); adjustPadding(); })
        .observe(window.parent.document.body, {childList: true, subtree: true});
    </script>
    """, height=0)


if __name__ == "__main__":
    main()

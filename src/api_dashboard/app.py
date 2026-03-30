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

/* ── LAYOUT ── */
.block-container {
    padding: 90px 3rem 4rem 3rem !important; /* Top padding for fixed navbar */
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
}

/* ── DESKTOP NAVBAR FIX STYLES ── */
.desktop-nav-container {
    pointer-events: none; /* Let clicks through unless on a button */
}

/* Ensure no "..." in nav buttons */
[data-testid="stHorizontalBlock"] button p {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
    font-size: 0.9rem !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(0,180,216,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── STATE ──────────────────────────────────────────────────────────────────────
logo_path = os.path.join(base_dir, "assets", "ZenPlannerLogo.png")

for key, default in [
    ('logged_in', False), ('user_name', ''), ('stress_level', None),
    ('study_plan', {}), ('profile_configured', False), ('user_profile', None),
    ('engine_msg', ''), ('subjects_list', []), ('current_page', 'dashboard')
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
    if plan:
        view_type = st.radio("Vista calendario", ["Visualizzazione Settimanale", "Focus Giornaliero"], horizontal=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if view_type == "Visualizzazione Settimanale":
            cols = st.columns(7)
            days = list(plan.keys())
            for i, d in enumerate(days):
                with cols[i]:
                    st.markdown(f"<div class='schedule-header'>{d[:3]}</div>", unsafe_allow_html=True)
                    for h in range(9, 18):
                        s = plan[d][h]
                        if s: st.markdown(f"<div class='schedule-card'>{s}</div>", unsafe_allow_html=True)
                        else: st.markdown("<div class='empty-slot'></div>", unsafe_allow_html=True)
        else:
            sel_day = st.selectbox("Seleziona Giorno", list(plan.keys()))
            day_slots = plan[sel_day]
            for h in range(9, 18):
                s = day_slots[h]
                if s: st.markdown(f"<div class='schedule-card' style='max-width:400px; margin:10px auto;'>{s}</div>", unsafe_allow_html=True)
                else: st.markdown("<div class='empty-slot' style='max-width:400px; margin:10px auto;'></div>", unsafe_allow_html=True)


# ─── NAVIGATION ─────────────────────────────────────────────────────────────────
def desktop_navbar():
    """Renders a stable, high-quality fixed top navbar for desktop."""
    page = st.session_state['current_page']
    
    # 1. Create a container for the navbar at the very top
    nav_container = st.container()
    with nav_container:
        st.markdown('<div class="desktop-nav-anchor"></div>', unsafe_allow_html=True)
        c_logo, c_dash, c_prof, c_plan = st.columns([1.5, 1, 1, 1])
        
        with c_logo:
            st.markdown("""
            <div style='display:flex; align-items:center; height:100%; padding-top:8px;'>
                <img src="assets/ZenPlannerLogo.png" id="logo" class="logo-glow" width="120" alt="Logo">
                <span style='font-family:Outfit,sans-serif; font-weight:800; font-size:1.1rem; color:#00E5FF; letter-spacing:1px;'>
                ZENPLANNER AI
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        with c_dash:
            is_active = page == "dashboard"
            if st.button("🏠 Dashboard", key="nav_dash", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['current_page'] = 'dashboard'; st.rerun()
        with c_prof:
            is_active = page == "profile"
            if st.button("👤 Profilo", key="nav_prof", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['current_page'] = 'profile'; st.rerun()
        with c_plan:
            is_active = page == "scheduler"
            if st.button("📅 Planner", key="nav_plan", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['current_page'] = 'scheduler'; st.rerun()

    # 2. Inject JS to make THIS specific container fixed to the top
    components.html("""
    <script>
    function applyNavbarRedesign() {
        const anchor = window.parent.document.querySelector('.desktop-nav-anchor');
        if (!anchor) return;
        
        const container = anchor.closest('[data-testid="stVerticalBlockBorderWrapper"]') 
                       || anchor.closest('[data-testid="stVerticalBlock"]');
        if (!container) return;

        // Reset and Apply Fixed Styles
        container.style.cssText = `
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            max-width: none !important;
            background: rgba(10, 15, 40, 0.85) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            z-index: 1000000 !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 12px 60px !important;
            display: flex !important;
            justify-content: center !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4) !important;
        `;
        
        // Target the column layout inside
        const colWrap = container.querySelector('[data-testid="stHorizontalBlock"]');
        if (colWrap) {
            colWrap.style.cssText = 'width: 100% !important; max-width: 1400px !important; display: flex !important; align-items: center !important;';
        }

        // Global styles for Navbar Buttons
        const buttons = container.querySelectorAll('button');
        buttons.forEach(btn => {
            const isPrimary = btn.getAttribute('kind') === 'primary';
            btn.style.cssText = `
                background: ${is_active ? 'rgba(0, 229, 255, 0.08)' : 'transparent'} !important;
                border: none !important;
                border-radius: 12px !important;
                color: ${isPrimary ? '#00E5FF' : 'rgba(255, 255, 255, 0.5)'} !important;
                font-family: Outfit, sans-serif !important;
                font-weight: 600 !important;
                letter-spacing: 0.3px !important;
                padding: 10px 24px !important;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                position: relative !important;
                overflow: visible !important;
              `;
            
            // Add indicator for active button
            if (isPrimary && !btn.querySelector('.nav-active-bar')) {
                const bar = document.createElement('div');
                bar.className = 'nav-active-bar';
                bar.style.cssText = 'position:absolute; bottom:-12px; left:25%; width:50%; height:3px; background:#00E5FF; border-radius:10px; box-shadow:0 0 10px rgba(0,229,255,0.6);';
                btn.appendChild(bar);
            }
        });
    }

    applyNavbarRedesign();
    setTimeout(applyNavbarRedesign, 100);
    setTimeout(applyNavbarRedesign, 500);
    new MutationObserver(applyNavbarRedesign).observe(window.parent.document.body, {childList: true, subtree: true});
    </script>
    """, height=0)


# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state['logged_in']:
        login_page()
        return

    desktop_navbar()

    page = st.session_state['current_page']
    if page == "dashboard":   view_dashboard()
    elif page == "profile":   view_profile()
    elif page == "scheduler": view_scheduler()
    else:                     view_dashboard()


if __name__ == "__main__":
    main()

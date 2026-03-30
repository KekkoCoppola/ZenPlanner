import streamlit as st
import pandas as pd
import sys
import os
import streamlit.components.v1 as components

# Aggiungiamo la root del progetto al path per importare correttamente il modulo src
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.csp_scheduler.domain import UserProfile, TimeSlot, StudySession
from src.csp_scheduler.scheduler import ZenSchedulerEngine

st.set_page_config(page_title="ZenPlanner", page_icon="🧘‍♂️", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Poppins:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; letter-spacing: -0.5px; }
    #MainMenu, footer, header { visibility: hidden; }

    .stApp {
        background: radial-gradient(circle at 10% 20%, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #E2E8F0;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .glass-card {
        background: rgba(25, 25, 35, 0.6);
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3); margin-bottom: 24px;
        animation: fadeUp 0.6s ease-out forwards;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-4px); border-color: #00E5FF; }
    .glass-card h3 { color: #00E5FF; margin-top: 0; font-size: 1.3rem; }
    .glass-card p.big-value { font-size: 2.8rem; font-weight: 800; color: #FFF; margin: 10px 0 0 0; text-shadow: 0 0 10px rgba(0,229,255,0.4); }

    .schedule-header {
        text-align: center; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.3rem;
        color: #FF9F1C; padding-bottom: 10px; border-bottom: 2px solid rgba(255,159,28,0.3); margin-bottom: 15px;
    }
    .schedule-card {
        background: linear-gradient(135deg, #4ea8de, #6930c3);
        color: #fff; padding: 12px 10px; border-radius: 12px; font-weight: 600; text-align: center;
        margin-bottom: 12px; font-size: 0.95rem; box-shadow: 0 6px 12px rgba(105,48,195,0.4);
        border: 1px solid rgba(255,255,255,0.2); animation: fadeUp 0.5s ease-out forwards;
        transition: all 0.3s ease; position: relative; overflow: hidden;
    }
    .schedule-card::after {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-25deg); animation: shimmer 3s infinite;
    }
    @keyframes shimmer { 0% { left: -100%; } 20% { left: 200%; } 100% { left: 200%; } }
    .schedule-card:hover { transform: scale(1.05) translateY(-2px); box-shadow: 0 10px 20px rgba(105,48,195,0.6); }

    .empty-slot {
        background-color: rgba(0,0,0,0.1); border: 1px dashed rgba(255,255,255,0.15);
        padding: 10px; border-radius: 12px; margin-bottom: 12px; height: 65px;
        transition: background-color 0.3s ease;
    }
    .empty-slot:hover { background-color: rgba(255,255,255,0.05); }

    [data-testid="stForm"] {
        background: rgba(25,25,35,0.6); backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08); border-radius: 16px;
        padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .stButton > button {
        background: rgba(20,30,61,0.7); backdrop-filter: blur(10px);
        color: #E2E8F0 !important; border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important; font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important; padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important; box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; background: rgba(114,9,183,0.6);
        border-color: #00B4D8 !important; box-shadow: 0 6px 15px rgba(114,9,183,0.4) !important;
        color: white !important;

    /* nav-marker hidden */
    .nav-marker { display: none; }
    .block-container { padding-bottom: 100px !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
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
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        st.markdown("<h1 style='text-align:center;'>Benvenuto in ZenPlanner</h1>"
                     "<p style='text-align:center; color:#00B4D8; margin-bottom:30px;'>"
                     "Intelligenza Artificiale per il tuo Benessere Accademico</p>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=True):
            name = st.text_input("Il tuo Nome")
            if st.form_submit_button("Accedi al Sistema", use_container_width=True) and name:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = name
                st.rerun()


def view_profile():
    st.markdown("<h1>Profilo Utente</h1>", unsafe_allow_html=True)
    st.markdown("Configura le tue abitudini per calibrare personalizzare il tuo piano.<br><br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Dati Fisici & Accademici")
        age = st.number_input("Età", min_value=18, max_value=80, value=22, step=1)
        sleep = st.number_input("Ore di Sonno medie/notte", min_value=3.0, max_value=14.0, value=7.0, step=0.5)
        study = st.number_input("Carico Studio Attuale (h/settimana)", min_value=0, max_value=80, value=20, step=1)
        gpa = st.number_input("Come valuti il tuo rendimento accademico (0-4)", min_value=0.0, max_value=4.0, value=3.0, step=0.1)
    with c2:
        st.markdown("### Routine e Sfide")
        social = st.number_input("Social Media (h/giorno)", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
        exercise = st.number_input("Attività Fisica (h/settimana)", min_value=0, max_value=40, value=3, step=1)
        family_support = st.number_input("Supporto Familiare (1-5)", min_value=1, max_value=5, value=3, step=1)
        financial_stress = st.number_input("Stress Finanziario (1-5)", min_value=1, max_value=5, value=3, step=1)
    with c3:
        st.markdown("### Pressioni Psicologiche")
        peer_pressure = st.number_input("Pressione Sociale (1-5)", min_value=1, max_value=5, value=3, step=1)
        relation_stress = st.number_input("Stress Relazionale (1-5)", min_value=1, max_value=5, value=2, step=1)
        diet_quality = st.number_input("Qualità Dieta (1-5)", min_value=1, max_value=5, value=3, step=1)

    st.markdown("### Cosa Fai Per Ridurre Lo Stress 🌿")
    coping_options = [
        "Esercizio", "Meditazione", "Lettura", "Social Media",
        "Passare Il Tempo In Solitaria", "Parlare con gli amici", "Viaggiare",
        "Passeggiare", "Guardare Sport", "Yoga"
    ]
    selected_coping = st.multiselect(
        "Seleziona le attività che svolgi abitualmente per gestire lo stress:",
        options=coping_options,
        default=[]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salva Profilo", use_container_width=True):
        # Convertiamo la selezione multiselect in una dict {'Coping_Activity': 1/0}
        coping_dict = {f"Coping_{opt}": (1 if opt in selected_coping else 0) for opt in coping_options}
        
        st.session_state['user_profile'] = UserProfile(
            age=age, gpa=gpa, social_media_hours_per_day=social, sleep_hours_per_night=sleep,
            physical_exercise_hours_per_week=exercise, family_support=family_support,
            financial_stress=financial_stress, peer_pressure=peer_pressure,
            relationship_stress=relation_stress, diet_quality=diet_quality, 
            coping_mechanisms=coping_dict
        )
        st.session_state['profile_configured'] = True
        st.success("✅ Profilo Salvato!.")


def view_scheduler():
    st.markdown("<h1>Generatore Piano Settimanale 🚀</h1>", unsafe_allow_html=True)

    if not st.session_state['profile_configured']:
        st.error("⚠️ Configura prima il tuo Profilo Utente per la generazione del piano!")
        return

    user = st.session_state.get('user_profile')
    if user is None:
        st.error("Il tuo profilo è obsoleto. Torna in Profilo Utente e premi Salva!")
        return

    st.markdown("### 📚 Inserimento Materie")
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    with c1: subj_name = st.text_input("Titolo Sessione / Materia")
    with c2: subj_hours = st.number_input("Ore necessarie", 1, 40, 5)
    with c3: subj_dead = st.selectbox("Scadenza Limite", ["Nessuna","Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"])
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add"):
            if subj_name:
                st.session_state['subjects_list'].append({"name": subj_name, "hours": subj_hours, "deadline": subj_dead})
                st.rerun()

    if st.session_state['subjects_list']:
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.markdown("**Coda di Elaborazione Attuale:**")
        for s in st.session_state['subjects_list']:
            deadline_text = f"⏳ Entro {s['deadline']}" if s['deadline'] != 'Nessuna' else ''
            st.markdown(f"🔹 **{s['name']}** &mdash; {s['hours']}h <span style='color:#FF9F1C; font-size:0.85rem;'>{deadline_text}</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Pulisci Lista Materie"):
            st.session_state['subjects_list'] = []
            st.rerun()

    if st.button("✨ Avvia Generazione Piano Di Studio", use_container_width=True):
        if not st.session_state['subjects_list']:
            st.warning("Nessuna materia fornita !")
            return

        engine = ZenSchedulerEngine(user)
        slots = [TimeSlot(day_of_week=d, start_time=h) for d in range(7) for h in range(9, 18)]

        planned_sessions = []
        days_map = {"Lunedì":0,"Martedì":1,"Mercoledì":2,"Giovedì":3,"Venerdì":4,"Sabato":5,"Domenica":6}
        for s in st.session_state['subjects_list']:
            dd = days_map.get(s['deadline'], None)
            for i in range(s['hours']):
                planned_sessions.append(StudySession(id=f"{s['name']}_hw{i+1}", subject=s['name'], deadline_day=dd))

        with st.spinner("L'Engine è in esplorazione dell'albero di ricerca..."):
            assignment, insight_msg = engine.generate_schedule(planned_sessions, slots)

        total_hours = sum(s['hours'] for s in st.session_state['subjects_list'])
        st.session_state['stress_level'] = engine.predict_baseline_stress(total_hours)
        st.session_state['engine_msg'] = insight_msg

        days = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
        plan = {day: {h: None for h in range(9, 18)} for day in days}

        if assignment:
            for session, slot in assignment.items():
                day_name = days[slot.day_of_week]
                plan[day_name][slot.start_time] = f"{slot.start_time:02d}:00 - {slot.start_time+1:02d}:00<br><b>{session.subject}</b>"
            st.session_state['study_plan'] = plan
            st.success("✅ Piano Generato! Puoi Visualizzarlo Nella Dashboard.")
        else:
            st.error("❌ Fallimento . Riduci il carico o allenta le scadenze!")
            st.session_state['study_plan'] = {}


def view_dashboard():
    st.markdown("<h1>Analytics & Calendario 📊</h1>", unsafe_allow_html=True)

    stress = st.session_state.get('stress_level')
    s_text = f"{stress:.2f}" if stress else "N/A"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="glass-card" style="text-align:center;"><h3>Predizione Stress Burnout</h3><p class="big-value">{s_text}</p></div>', unsafe_allow_html=True)
    with c2:
        total_blocks = sum(sum(1 for v in ds.values() if v is not None) for ds in st.session_state.get('study_plan', {}).values())
        st.markdown(f'<div class="glass-card" style="text-align:center;"><h3>Blocchi (1h) Allocati</h3><p class="big-value">{total_blocks}</p></div>', unsafe_allow_html=True)

    engine_msg = st.session_state.get('engine_msg')
    if engine_msg:
        st.markdown(f"<div style='background:rgba(255,159,28,0.2); border-left:4px solid #FF9F1C; padding:15px; border-radius:8px; margin-bottom:20px;'>🧠 ML: {engine_msg}</div>", unsafe_allow_html=True)

    plan = st.session_state.get('study_plan', {})
    if not plan:
        st.info("Piano non ancora generato.")
        return

    view_type = st.radio("Seleziona Vista", ["Visualizzazione Settimanale", "Focus Giornaliero"], horizontal=True)
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
                        st.markdown(f"<div class='empty-slot'></div>", unsafe_allow_html=True)
    else:
        c_sel, _ = st.columns([1, 2])
        with c_sel:
            day_selected = st.selectbox("Seleziona Giorno", list(plan.keys()))
        st.markdown(f"<h2 style='text-align:center; color:#FF9F1C;'>{day_selected}</h2>", unsafe_allow_html=True)
        day_slots = plan[day_selected]
        if not any(v is not None for v in day_slots.values()):
            st.markdown("<div style='text-align:center; opacity:0.6; padding:40px;'>Zen mode 🌿</div>", unsafe_allow_html=True)
        else:
            for h in range(9, 18):
                s = day_slots[h]
                if s:
                    st.markdown(f"<div class='schedule-card' style='max-width:350px; margin:10px auto; padding:20px;'>{s}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='empty-slot' style='max-width:350px; margin:10px auto;'></div>", unsafe_allow_html=True)


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

    # ── Fixed bottom navbar ──
    with st.container(border=True):
        st.markdown('<div class="nav-marker"></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            t = "primary" if page == "dashboard" else "secondary"
            if st.button("🏠 Dashboard", key="go_dash", use_container_width=True, type=t):
                st.session_state['current_page'] = 'dashboard'
                st.rerun()
        with c2:
            t = "primary" if page == "profile" else "secondary"
            if st.button("👤 Profilo", key="go_prof", use_container_width=True, type=t):
                st.session_state['current_page'] = 'profile'
                st.rerun()
        with c3:
            t = "primary" if page == "scheduler" else "secondary"
            if st.button("📅 Planner", key="go_sched", use_container_width=True, type=t):
                st.session_state['current_page'] = 'scheduler'
                st.rerun()

    # JavaScript to physically fix the navbar to the bottom of the viewport
    components.html("""
    <script>
    function fixNavbar() {
        var markers = window.parent.document.querySelectorAll('.nav-marker');
        if (markers.length > 0) {
            var m = markers[0];
            var container = m.closest('[data-testid="stVerticalBlockBorderWrapper"]') || m.closest('div[data-testid="stVerticalBlock"]');
            if (container) {
                container.style.cssText = `
                    position: fixed !important;
                    bottom: 0px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 350px;
                    max-width: 90vw;
                    background: rgba(12, 18, 40, 0.95);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 25px 25px 0 0;
                    padding: 8px 16px 14px 16px;
                    z-index: 999999;
                    box-shadow: 0 -5px 30px rgba(0,0,0,0.6);
                `;
                var btns = container.querySelectorAll('button');
                btns.forEach(function(btn) {
                    btn.style.cssText = `
                        background: transparent !important;
                        border: none !important;
                        box-shadow: none !important;
                        color: rgba(255,255,255,0.5);
                        font-size: 0.8rem;
                        padding: 8px 2px;
                        border-radius: 14px;
                        transition: all 0.25s ease;
                        min-height: 0;
                        width: 100%;
                    `;
                    // Forzo il div interno e il paragrafo a non spezzare la parola in verticale
                    var txtTags = btn.querySelectorAll('p, div, span');
                    txtTags.forEach(function(t) {
                        t.style.wordBreak = 'keep-all';
                        t.style.whiteSpace = 'nowrap';
                        t.style.overflow = 'hidden';
                        t.style.textOverflow = 'ellipsis';
                        t.style.fontSize = '0.75rem';
                        t.style.lineHeight = '1.1';
                    });
                    
                    // Detect if primary by checking the parent div's data-testid or the button kind
                    var parentDiv = btn.closest('[data-testid="baseButton-primary"]');
                    if (btn.getAttribute('kind') === 'primary' || parentDiv) {
                        btn.style.color = '#00B4D8 !important';
                        btn.style.background = 'rgba(0,180,216,0.18) !important';
                    }
                });
            }
        }
    }
    setTimeout(fixNavbar, 200);
    setTimeout(fixNavbar, 600);
    setTimeout(fixNavbar, 1200);
    new MutationObserver(fixNavbar).observe(window.parent.document.body, {childList: true, subtree: true});
    </script>
    """, height=0)


if __name__ == "__main__":
    main()

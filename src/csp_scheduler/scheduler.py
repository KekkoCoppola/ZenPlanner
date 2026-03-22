import os
import joblib
import warnings
import pandas as pd
from typing import List, Dict, Optional

from .domain import UserProfile, StudySession, TimeSlot
from .csp import CSP
from .constraints import NoOverlapConstraint, DailyMaxHoursConstraint, MaxConsecutiveConstraint, DeadlineConstraint
from .solver import CSPSolver

warnings.filterwarnings('ignore', category=UserWarning)

class ZenSchedulerEngine:
    """
    Facade principale del sistema.
    In questa architettura raffinata, il Machine Learning funge da "Root Gatekeeper"
    per valutare il carico di lavoro sistemico e fare tuning dei vincoli. 
    Il Solutore CSP usa euristiche interne (LCV) per distribuire perfettamente il carico 
    rispettando i giorni richiesti minimizzando la varianza.
    """
    def __init__(self, user_profile: UserProfile):
        self.user = user_profile
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")
        try:
            self.model = joblib.load(os.path.join(models_dir, "tuned_best_model.pkl"))
            self.scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
            try:
                self.model_features = joblib.load(os.path.join(models_dir, "model_features.pkl"))
            except FileNotFoundError:
                self.model_features = None
        except FileNotFoundError:
            self.model = None
            self.scaler = None
            self.model_features = None

    def predict_baseline_stress(self, total_study_hours: int) -> float:
        """ML Oracle Gatekeeper: calcola olisticamente l'impatto psicologico del volume richiesto."""
        if not self.model or not self.scaler: 
            raise RuntimeError("CRITICAL: model or scaler is None! Path is broken inside Streamlit context.")
        
        work_rest_ratio = total_study_hours / max((self.user.sleep_hours_per_night * 7), 1)
        social_ex = (self.user.social_media_hours_per_day * 7) / (self.user.physical_exercise_hours_per_week + 0.1)
        
        input_data = {
            'Age': [self.user.age],
            'Study Hours Per Week': [total_study_hours],
            'Social Media Usage (Hours per day)': [self.user.social_media_hours_per_day],
            'Sleep Duration (Hours per night)': [self.user.sleep_hours_per_night],
            'Physical Exercise (Hours per week)': [self.user.physical_exercise_hours_per_week],
            'Relationship Stress': [self.user.relationship_stress],
            'Work_Rest_Ratio': [work_rest_ratio],
            'Social_Exercise_Ratio': [social_ex]
        }
        
        # Aggiunta coping mechanisms
        if dict is not type(self.user.coping_mechanisms):
            input_data.update(self.user.coping_mechanisms) # type: ignore
        else:
            for k, v in self.user.coping_mechanisms.items():
                input_data[k] = [v]
            
        df = pd.DataFrame(input_data)
            
        try:
            # 1. Applica lo Scaler a TUTTE e 13 le feature numeriche
            if hasattr(self.scaler, 'feature_names_in_'):
                for col in self.scaler.feature_names_in_:
                    if col not in df.columns:
                        df[col] = 0
                df_scaled = df[self.scaler.feature_names_in_].copy()
                df_scaled.loc[:, :] = self.scaler.transform(df_scaled)
            else:
                df_scaled = df.copy()
                
            # 2. Poi, estrai SOLO le feature richieste dal modello (es. le 7 della RForest)
            if hasattr(self.model, 'feature_names_in_'):
                final_input = df_scaled[self.model.feature_names_in_]
            elif self.model_features:
                final_input = df_scaled[self.model_features]
            else:
                final_input = df_scaled
                
            # 3. Predizione effettiva
            prediction = self.model.predict(final_input)[0]
            return float(min(10.0, max(1.0, prediction)))
        except Exception as e:
            raise e

    def generate_schedule(self, planned_sessions: List[StudySession], available_slots: List[TimeSlot]) -> tuple[Optional[Dict[StudySession, TimeSlot]], str]:
        """
        Motore generativo. Mappa le variabili complesse (materie, priorità, scadenze) negli slot CSP.
        """
        total_hours_requested = len(planned_sessions)
        insight_msg = f"Volume richiesto: {total_hours_requested} sessioni. "
        
        # --- 1. COLLABORAZIONE OLISTICA ML -> AI ---
        predicted_stress = self.predict_baseline_stress(total_hours_requested)
        insight_msg += f"Stress ML predetto: {predicted_stress:.1f}/10. "
        
        dynamic_max_daily_hours = self.user.max_study_hours_per_day
        
        if predicted_stress > self.user.max_stress_tolerance:
            # HYPERPARAMETER TUNING DA PARTE DEL ML SERVER AL SIMBOLIC CSP
            dynamic_max_daily_hours = max(2, dynamic_max_daily_hours - 2)
            max_consecutive_hours = 1
            insight_msg += f"ALLARME Burnout. L'Oracolo forza tetto a {dynamic_max_daily_hours}h/giorno e stringhe di {max_consecutive_hours}h per imporre il riposo."
        else:
            max_consecutive_hours = 2
            insight_msg += f"Carico sano. Distribuzione adattiva attivata (max {max_consecutive_hours}h senza pause)."
            
        # --- 2. ISTANZIAZIONE CSP ---
        domains = {var: available_slots for var in planned_sessions}
        csp = CSP(planned_sessions, domains)
        
        # --- 3. INIEZIONE HARD CONSTRAINTS ---
        csp.add_constraint(NoOverlapConstraint(planned_sessions))
        csp.add_constraint(MaxConsecutiveConstraint(planned_sessions, max_consecutive_hours))
        for day in range(7):
            csp.add_constraint(DailyMaxHoursConstraint(planned_sessions, dynamic_max_daily_hours, day))
            
        # Dinamizzazione delle Scadenze (Rigid Constraints)
        has_deadlines = False
        for session in planned_sessions:
            if session.deadline_day is not None:
                csp.add_constraint(DeadlineConstraint(session))
                has_deadlines = True
                
        if has_deadlines:
            insight_msg += " Rilevati vincoli di scadenza rigidi: il Solver è in modalità ad alta restrizione."
            
        # --- 4. ENGINE E ESECUZIONE ---
        solver = CSPSolver(csp)
        return solver.backtracking_search(), insight_msg

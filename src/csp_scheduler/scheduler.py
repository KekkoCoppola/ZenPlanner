import os
import joblib
import warnings
import pandas as pd
from typing import List, Dict, Optional

from .domain import UserProfile, StudySession, TimeSlot
from .csp import CSP
from .constraints import NoOverlapConstraint, DailyMaxHoursConstraint
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
        if not self.model or not self.scaler: return 0.0
        
        work_rest_ratio = total_study_hours / max((self.user.sleep_hours_per_night * 7), 1)
        social_ex = (self.user.social_media_hours_per_day * 7) / (self.user.physical_exercise_hours_per_week + 0.1)
        
        input_data = {
            'Age': [self.user.age],
            'Academic Performance (GPA)': [self.user.gpa],
            'Study Hours Per Week': [total_study_hours],
            'Social Media Usage (Hours per day)': [self.user.social_media_hours_per_day],
            'Sleep Duration (Hours per night)': [self.user.sleep_hours_per_night],
            'Physical Exercise (Hours per week)': [self.user.physical_exercise_hours_per_week],
            'Family Support': [self.user.family_support],
            'Financial Stress': [self.user.financial_stress],
            'Peer Pressure': [self.user.peer_pressure],
            'Relationship Stress': [self.user.relationship_stress],
            'Diet Quality': [self.user.diet_quality],
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
        if self.model_features:
            for col in self.model_features:
                if col not in df.columns: df[col] = 0
            df = df[self.model_features]
            
        try:
            numeric_cols = getattr(self.scaler, 'feature_names_in_', df.columns[:13])
            cols_to_scale = [c for c in numeric_cols if c in df.columns]
            df[cols_to_scale] = self.scaler.transform(df[cols_to_scale])
            return float(self.model.predict(df)[0])
        except Exception:
            return 0.0

    def generate_schedule(self, subjects: Dict[str, int], available_slots: List[TimeSlot]) -> tuple[Optional[Dict[StudySession, TimeSlot]], str]:
        """
        Motore generativo.
        Ritorna una tupla: (Assegnamento, Messaggio/Insight del Machine Learning).
        """
        total_hours_requested = sum(subjects.values())
        insight_msg = f"Volume richiesto: {total_hours_requested} ore. "
        
        # --- 1. COLLABORAZIONE OLISTICA ML -> AI ---
        predicted_stress = self.predict_baseline_stress(total_hours_requested)
        insight_msg += f"Lo Stress Oracolare predetto e' {predicted_stress:.1f}/10. "
        
        dynamic_max_daily_hours = self.user.max_study_hours_per_day
        
        if predicted_stress > self.user.max_stress_tolerance:
            # HYPERPARAMETER TUNING DA PARTE DEL ML SERVER AL SIMBOLIC CSP
            dynamic_max_daily_hours = max(2, dynamic_max_daily_hours - 2)
            insight_msg += f"ALLARME: Soglia superata. L'AI ha forzato un abbassamento del tetto giornaliero a {dynamic_max_daily_hours}h per diluire obbligatoriamente il carico."
        else:
            insight_msg += "Carico sano. Procedo con la distribuzione ottimizzata."
            
        # --- 2. ISTANZIAZIONE CSP ---
        variables = []
        for subj, hours in subjects.items():
            for i in range(hours):
                variables.append(StudySession(id=f"{subj}_{i+1}", subject=subj))
                
        domains = {var: available_slots for var in variables}
        csp = CSP(variables, domains)
        
        # --- 3. INIEZIONE HARD CONSTRAINTS ---
        csp.add_constraint(NoOverlapConstraint(variables))
        for day in range(7):
            csp.add_constraint(DailyMaxHoursConstraint(variables, dynamic_max_daily_hours, day))
            
        # --- 4. ENGINE E ESECUZIONE ---
        solver = CSPSolver(csp)
        return solver.backtracking_search(), insight_msg

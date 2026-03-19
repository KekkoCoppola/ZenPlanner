import os
import warnings
import pandas as pd
import joblib
from typing import Dict, List

from .csp import Constraint
from .domain import StudySession, TimeSlot, UserProfile

# Suppress scikit-learn warnings about absent feature names during scaling
warnings.filterwarnings('ignore', category=UserWarning)

# ==========================================
# HARD CONSTRAINTS (Vincoli matematici fisici)
# ==========================================

class NoOverlapConstraint(Constraint[StudySession, TimeSlot]):
    """
    Assicura che non ci siano due sessioni di studio programmate nello stesso slot orario.
    """
    def __init__(self, variables: List[StudySession]):
        super().__init__(variables)
        
    def satisfied(self, assignment: Dict[StudySession, TimeSlot]) -> bool:
        # Conta quanti slot unici sono stati assegnati.
        assigned_slots = list(assignment.values())
        return len(assigned_slots) == len(set(assigned_slots))


class DeadlineConstraint(Constraint[StudySession, TimeSlot]):
    """
    Assicura che la sessione sia completata prima o nello stesso giorno della sua scadenza.
    """
    def __init__(self, variable: StudySession):
        super().__init__([variable])
        self.session = variable
        
    def satisfied(self, assignment: Dict[StudySession, TimeSlot]) -> bool:
        if self.session not in assignment:
            return True # Non ancora assegnata -> non viola il vincolo
        
        slot = assignment[self.session]
        if self.session.deadline_day is not None:
            return slot.day_of_week <= self.session.deadline_day
        return True


class DailyMaxHoursConstraint(Constraint[StudySession, TimeSlot]):
    """
    Assicura che le sessioni assegnate in un certo giorno non superino il carico massimo.
    """
    def __init__(self, variables: List[StudySession], max_hours: int, day: int):
        super().__init__(variables)
        self.max_hours = max_hours
        self.day = day
        
    def satisfied(self, assignment: Dict[StudySession, TimeSlot]) -> bool:
        day_sessions_count = sum(
            1 for sess, slot in assignment.items()
            if slot.day_of_week == self.day and sess in self.variables
        )
        return day_sessions_count <= self.max_hours


# ==========================================
# SOFT CONSTRAINTS (Tolleranza Psivofisica via ML Oracle)
# ==========================================

class MLStressOracleConstraint(Constraint[StudySession, TimeSlot]):
    """
    Ponte architetturale Ibrido tra il Solver Discreto e l'algoritmo Connessionista.
    Ogni nodo parziale valutato dal CSP interroga questo oracolo. Se lo stress
    previsto supera la soglia di tolleranza, causa il backtracking del motore.
    """
    def __init__(self, variables: List[StudySession], user_profile: UserProfile):
        super().__init__(variables)
        self.user = user_profile
        
        # Inizializza i path assoluti sicuri verso il modulo ML
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")
        
        try:
            self.model = joblib.load(os.path.join(models_dir, "tuned_best_model.pkl"))
            self.scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
            try:
                # Carichiamo le model_features esatte usate nel fit per allineare le colonne
                self.model_features = joblib.load(os.path.join(models_dir, "model_features.pkl"))
            except:
                self.model_features = None
        except FileNotFoundError:
            # Il sistema e' robusto: se i modelli non sono ancora pre-calcolati, l'oracolo dorme.
            self.model = None
            self.scaler = None

    def satisfied(self, assignment: Dict[StudySession, TimeSlot]) -> bool:
        # Fallback in assenza di modelli
        if not self.model or not self.scaler:
            return True
            
        # 1. ESTREARRE FEATURE DINAMICHE DALL'ALBERO CSP CORRENTE
        # Calcolo istantaneo delle ore di studio "simulate" in questo piano parziale
        simulated_study_hours = len(assignment) # (Assumiamo sessioni fisse da 1h)
        
        if simulated_study_hours == 0:
            return True
            
        # 2. FEATURE ENGINEERING DINAMICO (ricalcolato sul piano di studio corrente)
        work_rest_ratio = simulated_study_hours / max((self.user.sleep_hours_per_night * 7), 1)
        social_exercise_ratio = (self.user.social_media_hours_per_day * 7) / (self.user.physical_exercise_hours_per_week + 0.1)

        # 3. ASSEMBLA IL VETTORE DI PREDIZIONE (Profilo Utente Statico + Dinamiche Simulate)
        input_data = {
            'Age': [self.user.age],
            'Academic Performance (GPA)': [self.user.gpa],
            'Study Hours Per Week': [simulated_study_hours],
            'Social Media Usage (Hours per day)': [self.user.social_media_hours_per_day],
            'Sleep Duration (Hours per night)': [self.user.sleep_hours_per_night],
            'Physical Exercise (Hours per week)': [self.user.physical_exercise_hours_per_week],
            'Family Support': [self.user.family_support],
            'Financial Stress': [self.user.financial_stress],
            'Peer Pressure': [self.user.peer_pressure],
            'Relationship Stress': [self.user.relationship_stress],
            'Diet Quality': [self.user.diet_quality],
            'Work_Rest_Ratio': [work_rest_ratio],
            'Social_Exercise_Ratio': [social_exercise_ratio]
        }
        
        # Aggiunta encoding del Coping Mechanism dal form preferenze Utente
        if dict is not type(self.user.coping_mechanisms):
             input_data.update(self.user.coping_mechanisms) # type: ignore
        else:
             for k, v in self.user.coping_mechanisms.items():
                  input_data[k] = [v]
            
        df_input = pd.DataFrame(input_data)
        
        # Allineamento colonne (per evitare crash di mismatch con il Random Forest/XGBoost)
        if self.model_features is not None:
             for col in self.model_features:
                  if col not in df_input.columns:
                       df_input[col] = 0
             df_input = df_input[self.model_features]

        # 4. DATA SCALING
        try:
            if hasattr(self.scaler, 'feature_names_in_'):
                numeric_cols = self.scaler.feature_names_in_
            else:
                numeric_cols = ['Age', 'Academic Performance (GPA)', 'Study Hours Per Week', 'Social Media Usage (Hours per day)', 'Sleep Duration (Hours per night)', 'Physical Exercise (Hours per week)', 'Family Support', 'Financial Stress', 'Peer Pressure', 'Relationship Stress', 'Diet Quality', 'Work_Rest_Ratio', 'Social_Exercise_Ratio']
            
            numeric_cols = [c for c in numeric_cols if c in df_input.columns]
            if numeric_cols:
                df_input[numeric_cols] = self.scaler.transform(df_input[numeric_cols])
        except Exception:
            pass # Continua con i dati raw se c'e' una anomalia di cast
            
        # 5. PREDIZIONE ORACLE
        try:
            predicted_stress = self.model.predict(df_input)[0]
        except Exception:
            predicted_stress = 0.0

        # Il vincolo fallisce scatenando il Branch Pruning se lo stress e' tossico
        return predicted_stress <= self.user.max_stress_tolerance

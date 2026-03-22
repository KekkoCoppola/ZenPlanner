from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class UserProfile:
    """Rappresenta le variabili d'ambiente fisse per l'Oracolo ML."""
    age: int
    social_media_hours_per_day: float
    sleep_hours_per_night: float
    physical_exercise_hours_per_week: float
    relationship_stress: int       # Scala 1-5
    coping_mechanisms: Dict[str, int] # es. {'Coping_Meditation': 1, 'Coping_Exercise': 0, ...}
    
    # Preferenze addizionali hard-constraints
    max_study_hours_per_day: int = 8
    max_stress_tolerance: float = 6.0 # Soglia sopra la quale l'Oracolo applica il taglio (backtracking)

@dataclass(frozen=True)
class TimeSlot:
    """
    Rappresenta un Valore del Dominio. Uno slot orario atomico.
    Immutable (frozen=True) poiche' verra' usato come Valore mappato nella dict di assegnamento.
    """
    day_of_week: int  # 0 = Lunedi, 6 = Domenica
    start_time: int   # Ora di inizio, 0-23
    
    def __lt__(self, other):
        # Permette l'ordinamento naturale degli slot nel calendario
        if self.day_of_week == other.day_of_week:
            return self.start_time < other.start_time
        return self.day_of_week < other.day_of_week
        
    def __str__(self):
        days = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom']
        return f"{days[self.day_of_week]} {self.start_time}:00"

@dataclass(frozen=True)
class StudySession:
    """
    Rappresenta una singola Variabile nel CSP.
    Immutable (frozen=True) poiche' verra' usato come Chiave nella dict di assegnamento.
    """
    id: str           # Identificativo unico (es. 'Matematica_Chunck_1')
    subject: str      # Materia
    priority: int = 1 # 1: Alta priorita', 3: Bassa priorita'
    deadline_day: Optional[int] = None # Giorno entro cui la sessione DEVE essere completata
    
    def __str__(self):
        return f"{self.subject} ({self.id})"

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


class MaxConsecutiveConstraint(Constraint[StudySession, TimeSlot]):
    """
    Assicura che non ci siano più di 'max_consec' ore di studio ininterrotte consecutivamente.
    Implicita la creazione di "buchi" (pause zen) tra blocchi intensivi.
    """
    def __init__(self, variables: List[StudySession], max_consec: int):
        super().__init__(variables)
        self.max_consec = max_consec
        
    def satisfied(self, assignment: Dict[StudySession, TimeSlot]) -> bool:
        # Raduniamo per giorni
        days_slots = {}
        for slot in assignment.values():
            if slot.day_of_week not in days_slots:
                days_slots[slot.day_of_week] = []
            days_slots[slot.day_of_week].append(slot.start_time)
            
        # Conteggio contiguità formale
        for hours in days_slots.values():
            if not hours: continue
            sorted_hours = sorted(hours)
            consec = 1
            for i in range(len(sorted_hours) - 1):
                if sorted_hours[i+1] - sorted_hours[i] == 1:
                    consec += 1
                    if consec > self.max_consec:
                        return False
                else:
                    consec = 1 # resetta contatore alla pausa
        return True

from typing import Dict, List, Optional, TypeVar
from .csp import CSP

V = TypeVar('V')
D = TypeVar('D')

class CSPSolver:
    """
    Risolutore del CSP basato su ricerca in profondità (Depth-First Search) con Backtracking.
    Implementa euristiche di ottimizzazione avanzate richieste per i sistemi AI: MRV.
    """
    def __init__(self, csp: CSP[V, D]):
        self.csp = csp
        
    def backtracking_search(self) -> Optional[Dict[V, D]]:
        """
        Avvia la ricerca di una soluzione partendo da un assegnamento vuoto.
        Ritorna un dizionario con l'assegnamento finale {Variabile: Valore} se trova una soluzione, 
        altrimenti None se il problema è insoddisfacibile (scadenza non rispettabile o parametri troppo stringenti).
        """
        return self.backtrack({})
        
    def backtrack(self, assignment: Dict[V, D]) -> Optional[Dict[V, D]]:
        # Condizione di Terminazione: tutte le variabili hanno un valore
        if len(assignment) == len(self.csp.variables):
            return assignment
            
        # 1. RECUPERO VARIABILI (Euristica MRV)
        unassigned: List[V] = [v for v in self.csp.variables if v not in assignment]
        
        # Scelta intelligente della prossima variabile da elaborare
        first = self._select_unassigned_variable_mrv(unassigned, assignment)
        
        # 2. RICERCA E SCORRIMENTO DEI DOMINI (Euristica LCV)
        # LCV (Least Constraining Value) per CRAMMING AVOIDANCE (Minimum Variance):
        # Invece di iterare cronologicamente, calcoliamo quante ore sono già state assegnate
        # a ciascun giorno nel piano parziale. Ordiniamo i TimeSlot disponibili partendo
        # dai giorni attualmente più "scarichi". Questo bilancia automaticamente la
        # distribuzione scartando concentrazioni tossiche e spalmandole per natura!
        
        day_loads = {day: 0 for day in range(7)}
        for session, assigned_slot in assignment.items():
            day_loads[assigned_slot.day_of_week] += 1
            
        ordered_domain = sorted(
            self.csp.domains[first],
            key=lambda slot: (day_loads[slot.day_of_week], slot.start_time)
        )
        
        for value in ordered_domain:
            # Simulator: copiamo l'assegnamento e testiamo il valore parziale
            local_assignment = assignment.copy()
            local_assignment[first] = value
            
            # FORWARD CHECKING / CONSISTENCY CHECK
            # Il CSP interroga localmente tutti i vincoli (NoOverlap, MLOracle, ecc.)
            if self.csp.consistent(first, local_assignment):
                # Ricorsione: scendiamo più in profondità nell'albero
                result = self.backtrack(local_assignment)
                
                # Se il ramo ricorsivo non ha restituito None, abbiamo la soluzione
                if result is not None:
                    return result
                    
        # BACKTRACKING: Se siamo qui, nessun valore del dominio per 'first' ha funzionato.
        # Risaliamo nell'albero e proviamo a cambiare la variabile precedente.
        return None
        
    def _select_unassigned_variable_mrv(self, unassigned: List[V], assignment: Dict[V, D]) -> V:
        """
        Euristica: Minimum Remaining Values (MRV).
        Sceglie la variabile che ha il minor numero di valori di dominio "legali" rimasti.
        """
        def count_consistent(var: V) -> int:
            count = 0
            for val in self.csp.domains[var]:
                test_assign = assignment.copy()
                test_assign[var] = val
                if self.csp.consistent(var, test_assign):
                    count += 1
            return count
            
        # Ritorna la variabile col punteggio (numero di mosse valide) più basso
        return min(unassigned, key=count_consistent)

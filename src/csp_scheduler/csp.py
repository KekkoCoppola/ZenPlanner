from typing import Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod

V = TypeVar('V')  # Tipo di Variabile (es. variabile: sessione di studio)
D = TypeVar('D')  # Tipo di Dominio (es. dominio: slot orario)

class Constraint(Generic[V, D], ABC):
    """
    Classe astratta base per un Vincolo.
    Definisce l'interfaccia matematica per i vincoli del CSP.
    """
    def __init__(self, variables: List[V]):
        # Le variabili su cui agisce questo vincolo
        self.variables = variables
        
    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        """
        Controlla se il vincolo è soddisfatto dato l'assegnamento corrente.
        :param assignment: un dizionario che associa le variabili a valori del dominio.
        """
        pass

class CSP(Generic[V, D]):
    """
    Motore astratto per il Constraint Satisfaction Problem.
    Gestisce Variabili, Domini e una coda di Vincoli.
    """
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]):
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Incoerenza: ogni variabile definita deve avere un dominio assegnato.")

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        """Aggiunge un vincolo iterando sulle sue variabili target."""
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Incoerenza: il vincolo fa riferimento a una variabile non nel CSP.")
            self.constraints[variable].append(constraint)

    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        """
        Controlla se il valore appena assegnato a 'variable'
        viola qualche vincolo in 'assignment'.
        """
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

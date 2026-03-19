# ZenPlanner

ZenPlanner è uno scheduler adattivo intelligente progettato per ottimizzare lo studio e preservare l'equilibrio psicofisico (salute mentale).

A differenza dei tradizionali pianificatori statici, ZenPlanner adotta un'architettura ibrida e modulare che combina **Intelligenza Artificiale Simbolica (CSP)** e **Machine Learning (Regressione Predictiva)**. Il sistema genera dinamicamente un piano di studi settimanale che bilancia il carico didattico, massimizzando il rendimento nel rispetto dei limiti di stress individuali.

## Architettura Ibrida: CSP + Oracolo ML

Il core del progetto si basa su un'interazione avanzata tra due motori:

1. **CSP Scheduler (Constraint Satisfaction Problem)**: 
   Attraverso algoritmi di ricerca (Backtracking DFS con Forward Checking ed euristiche MRV/LCV), il CSP esplora le combinazioni temporali per allocare le sessioni di studio. Garantisce un piano corretto rispettando vincoli strutturali (hard constraints) come scadenze, nessuna sovrapposizione e tetto massimo di ore libere.

2. **Oracolo ML (Machine Learning Gatekeeper)**:
   Agisce alla radice dell'albero di ricerca: valutando olisticamente il profilo studente e il monte ore totale richiesto, effettua una predizione dello stress a monte. Se rileva rischio di burnout, collabora innescando un meccanismo di *Hyperparameter Tuning* automatico per il CSP, imponendo vincoli geometrici più stringenti (es. restringendo il Tetto Giornaliero Massimo) per forzare matematicamente la diluizione della fatica e proteggere la salute mentale.

**Vincoli architetturali implementati:**
- **NoOverlapConstraint**: (Hard constraint) Previene accavallamenti temporali tra le sessioni di studio.
- **DeadlineConstraint**: (Hard constraint) Garantisce che ogni singola materia venga distribuita temporalmente sempre in anticipo rispetto alla data dell'esame.
- **DailyMaxHoursConstraint**: (Hard constraint) Protezione del carico didattico dinamica.

**Motore Algoritmico (Solver AI):**
- **Depth-First Backtracking Search**: Esplorazione ricorsiva dell'albero delle soluzioni (Fail-First).
- **Euristica MRV (Minimum Remaining Values)**: Seleziona per prime le sessioni più difficili da allocare, riducendo drasticamente il tempo di ricerca (pruning logico).
- **Euristica LCV (Least Constraining Value)**: Ordinamento intelligente del dominio. Calcolando dinamicamente il carico sui vari giorni durante la generazione del piano, il LCV predilige i "giorni più scarichi", operando matematicamente come un ottimizzatore per *minimizzare la varianza* del carico settimanale, senza ricorrere a complessi risolutori COP continui.

## Struttura della Repository

Il progetto è suddiviso per dominio:

- `src/ml_pipeline/`: Data Science & Modelli. Contiene gli script operativi industriali (es. corretta divisione train/test contro data-leakage e gestione dei missing value), feature engineering e training.
- `src/csp_scheduler/`: Algorithm Layer. Logica per la mappatura del CSP ibrido, modellazione delle Variabili, Domini e ricerca con l'Oracolo.
- `src/api_dashboard/`: User Interface & Gateway. L'infrastruttura front-end (es. Streamlit) per input utente/visualizzazione.
- `analytics/`: Directory adibita alle elaborazioni grafiche delle performance ML (es. distribuzioni e top feature importance).
- `data/`: Dati sorgente per i training e output scalati in pre-elaborazione.
- `tests/`: Suite logica per testare pipeline e validazioni algoritmi (pytest).

## Setup Veloce

```bash
# 1. Installare le dipendenze fornite
pip install -r requirements.txt

# 2. Innescare la pulizia dei dati e addestrare i modelli per generare l'oracolo
python src/ml_pipeline/preprocess_data.py
python src/ml_pipeline/train_model.py
```

# ZenPlanner

ZenPlanner è uno scheduler adattivo intelligente progettato per ottimizzare lo studio e preservare l'equilibrio psicofisico (salute mentale).

A differenza dei tradizionali pianificatori statici, ZenPlanner adotta un'architettura ibrida e modulare che combina **Intelligenza Artificiale Simbolica (CSP)** e **Machine Learning (Regressione Predictiva)**. Il sistema genera dinamicamente un piano di studi settimanale che bilancia il carico didattico, massimizzando il rendimento nel rispetto dei limiti di stress individuali.

## Architettura Ibrida: CSP + Oracolo ML

Il core del progetto si basa su un'interazione avanzata tra due motori:

1. **CSP Scheduler (Constraint Satisfaction Problem)**: 
   Attraverso algoritmi di ricerca (Backtracking DFS con Forward Checking ed euristiche MRV/LCV), il CSP esplora le combinazioni temporali per allocare le sessioni di studio. Garantisce un piano corretto rispettando vincoli strutturali (hard constraints) come scadenze, nessuna sovrapposizione e tetto massimo di ore libere.

2. **Oracolo ML (Machine Learning Stress Predictor)**:
   Mentre il CSP elabora i potenziali orari, modella temporaneamente le abitudini dell'utente in quel preciso piano (generando metriche come il discriminante `Work_Rest_Ratio`). Questi vettori, arricchiti con il profilo base dell'utente (impegni fissi, abitudini di fitness o diete, meccanismi di coping), vengono interrogati su un modello ML supervisionato pre-addestrato (Random Forest/XGBoost). 
   
   Il ML funge da *Funzione Obiettivo (Oracolo)* valutando lo stress generato specifico di quel piano (da 1 a 10). Se il punteggio sfora la soglia fisiologica consentita, il CSP applica il backtracking immediato: taglia il ramo schedulato e impone pause o redistribuisce la fatica, garantendo come output finale l'orario più salubre.

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

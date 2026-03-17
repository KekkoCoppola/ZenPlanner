# ZenPlanner
uno scheduler adattivo che bilancia studio e salute mentale. Integra Machine Learning (per predire la resilienza cognitiva giornaliera) e un Algoritmo Genetico/CSP per l'ottimizzazione oraria. Il sistema evolve dinamicamente le sessioni di studio, massimizzando il rendimento accademico nel rispetto dei vincoli di stress individuali pre-calcolati.

## Architettura del Progetto

Il progetto è modulare ed è diviso come segue:
- `data/`: Contiene i dataset, come `Student_Mental_Stress_and_Coping_Mechanisms.csv` (ignorato su Git se di grandi dimensioni).
- `src/ml_pipeline/`: Modulo del Data Scientist. Script per EDA, preprocessing e modelli ML.
- `src/csp_scheduler/`: Modulo dell'Algorithm Engineer. Contiene la logica per allocazione temporale CSP e backtracking.
- `src/api_dashboard/`: Modulo del Fullstack Dev. Contiene l'infrastruttura di front-end/UI (es. Streamlit).
- `tests/`: Contiene i test script (pytest) per validare moduli e algoritmi.

## Setup Iniziale dell'Ambiente (Per Sviluppatori)

Tutti i membri del team dovrebbero clonare la repo ed eseguire il seguente comando per installare le librerie fondamentali:

```bash
# Creazione e attivazione del virtual environment (raccomandato)
python -m venv venv
# Su Windows: venv\Scripts\activate
# Su Mac/Linux: source venv/bin/activate

# Installazione dei requisiti
pip install -r requirements.txt
```

## Flusso di Lavoro (Git branching)
Ognuno svilupperà sul proprio branch designato (es. `feature/ml-pipeline`, `feature/csp-scheduler`, `feature/dashboard`). Terminato lo sviluppo locale, si aprirà una Pull Request verso `main`.

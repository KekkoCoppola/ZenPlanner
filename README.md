# ZenPlanner
uno scheduler adattivo che bilancia studio e salute mentale. Integra Machine Learning (per predire la resilienza cognitiva giornaliera) e un Algoritmo Genetico/CSP per l'ottimizzazione oraria. Il sistema evolve dinamicamente le sessioni di studio, massimizzando il rendimento accademico nel rispetto dei vincoli di stress individuali pre-calcolati.

## Architettura del Progetto

Il progetto è modulare ed è diviso come segue:
- `assets/`: Contiene gli asset, come `ZenPlannerLogo.png`.
- `data/`: Contiene i dataset, come `Student_Mental_Stress_and_Coping_Mechanisms.csv`.
- `src/ml_pipeline/`: Modulo del Data Scientist. Script per EDA, preprocessing e modelli ML.
- `src/csp_scheduler/`: Modulo dell'Algorithm Engineer. Contiene la logica per allocazione temporale CSP e backtracking.
- `src/api_dashboard/`: Modulo del Fullstack Dev. Contiene l'infrastruttura di front-end/UI (es. Streamlit).
- `tests/`: Contiene i test script (pytest) per validare moduli e algoritmi.

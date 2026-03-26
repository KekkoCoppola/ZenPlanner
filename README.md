<p align="center">
  <img src="assets/ZenPlannerLogo.png" width="220" alt="ZenPlanner Logo">
</p>

<h1 align="center">🧘 ZenPlanner</h1>

<p align="center">
  <b>Scheduler Adattivo Intelligente per Studenti</b><br>
  <i>Ottimizzazione del tempo, prevenzione dello stress e Machine Learning</i>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/KekkoCoppola/ZenPlanner?style=flat-square&color=5D5CDE" alt="License" />
  <img src="https://img.shields.io/github/stars/KekkoCoppola/ZenPlanner?style=flat-square&color=5D5CDE" alt="Stars" />
  <img src="https://img.shields.io/github/languages/top/KekkoCoppola/ZenPlanner?style=flat-square&color=5D5CDE" alt="Top Language" />
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white" alt="Python Version" />
</p>

---

## 🚀 Prova l'App

Vuoi vedere ZenPlanner in azione? Accedi alla demo live direttamente nel tuo browser:

<p align="center">
  <a href="https://kekkocoppola.github.io/ZenPlanner/">
    <img src="https://img.shields.io/badge/APRI_ZENPLANNER-LIVE_DEMO-2ea44f?style=for-the-badge&logo=googlechrome&logoColor=white&labelColor=1a1a1a" alt="Live Demo" />
  </a>
</p>

---

## 🌟 Visione del Progetto

ZenPlanner non è un semplice calendario. È un assistente basato su **Intelligenza Artificiale** progettato per bilanciare il carico accademico con il benessere mentale. Attraverso un modello di **Machine Learning** (Random Forest Regressor) analizziamo il tuo profilo di stress e adattiamo dinamicamente un motore di **Constraint Satisfaction Problem (CSP)** per generare il piano di studio perfetto per te.

### ✨ Caratteristiche Principali

- 🧠 **Oracolo ML**: Predizione del burnout basata su 13 feature comportamentali.
- ⚙️ **Motore CSP Adattivo**: Generazione di scheduling con euristiche Fail-First (MRV) e Least Constraining Value (LCV).
- 🛡️ **Zen Gaps**: Inserimento automatico di pause basato sul tuo livello di stress predetto.
- 📊 **Dashboard Interattiva**: Gestione intuitiva di task, scadenze e priorità in tempo reale.

---

## 🏗️ Architettura Ibrida

Il core del progetto si basa su un'interazione **bidirezionale** tra l'analisi predittiva e la risoluzione dei vincoli:

```mermaid
graph TB
    subgraph Frontend ["🖥️ Streamlit Dashboard"]
        UI["Input Utente (Profilo + Materie)"]
    end
    
    subgraph ML ["🧠 ML Oracle (Gatekeeper)"]
        SCALER["StandardScaler (13 features)"]
        MODEL["Random Forest Regressor"]
        STRESS["Predizione Stress (0-10)"]
        SCALER --> MODEL --> STRESS
    end
    
    subgraph CSP_ENGINE ["⚙️ CSP Solver Engine"]
        CSP["CSP Framework (Variabili + Domini)"]
        CONSTRAINTS["Hard Constraints"]
        SOLVER["DFS Backtracking + MRV + LCV"]
        CSP --> CONSTRAINTS --> SOLVER
    end
    
    UI --> ML
    STRESS -->|"Hyperparameter Tuning (max_daily, max_consec)"| CSP_ENGINE
    SOLVER -->|"Piano Settimanale Ottimizzato"| Frontend
```

### 🧠 Dettagli del Motore CSP

| Componente | Funzione | Strategia |
|:---:|:---|:---|
| **Variabili** | Slot Temporali | Giorno × Ora (atomico) |
| **Domini** | Sessioni di Studio | Dinamici in base alla priorità |
| **Euristica Selezione** | **MRV** | Minimizzazione dei valori residui per pruning veloce |
| **Euristica Valore** | **LCV** | Minimizzazione della varianza oraria settimanale |
| **Vincoli** | Hard Constraints | Scadenze, No-Overlap, Daily Max, Contiguità |

---

## 📁 Struttura della Repository

```bash
ZenPlanner/
├── 📊 analytics/              # Grafici RMSE, Feature Importance e SHAP
├── 🎨 assets/                 # Brand identity e risorse grafiche
├── 💾 data/                   # Dataset originali e preprocessati
├── 📂 src/
│   ├── 🧠 ml_pipeline/        # Training, Preprocessing e XAI
│   ├── ⚙️ csp_scheduler/      # Motore CSP e Logic Layer
│   └── 🖥️ api_dashboard/      # Frontend Streamlit (app.py)
├── 🧪 tests/                  # Suite di test automatizzati
└── 📄 requirements.txt        # Dipendenze del progetto
```

---

## ⚡ Setup Veloce

Per eseguire ZenPlanner localmente, segui questi passaggi:

```bash
# 1. Clona il repository
git clone https://github.com/KekkoCoppola/ZenPlanner.git
cd ZenPlanner

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Addestra il modello (necessario al primo avvio)
python src/ml_pipeline/preprocess_data.py
python src/ml_pipeline/train_model.py

# 4. Lancia la Dashboard
streamlit run src/api_dashboard/app.py
```

---

## 👥 Il Nostro Team

Studenti di Informatica presso l'**Università degli Studi di Salerno**.

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/KekkoCoppola">
        <img src="https://github.com/KekkoCoppola.png" width="100px;" alt="Francesco Coppola" style="border-radius: 50%; border: 2px solid #5D5CDE;"/><br />
        <sub><b>Francesco Coppola</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/rosx3">
        <img src="https://github.com/rosx3.png" width="100px;" alt="Rosaria Cervino" style="border-radius: 50%; border: 2px solid #5D5CDE;"/><br />
        <sub><b>Rosaria Cervino</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/elesshhhh">
        <img src="https://github.com/elesshhhh.png" width="100px;" alt="Elena Carlomagno" style="border-radius: 50%; border: 2px solid #5D5CDE;"/><br />
        <sub><b>Elena Carlomagno</b></sub>
      </a>
    </td>
  </tr>
</table>

---
<p align="center">Made with ❤️ by ZenPlanner Team</p>

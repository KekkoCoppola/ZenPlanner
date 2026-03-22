import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
import shap
import warnings

# Ignoriamo i FutureWarning delle librerie grafiche per pulizia console
warnings.filterwarnings('ignore')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "data", "processed")
    analytics_dir = os.path.join(base_dir, "analytics")
    os.makedirs(analytics_dir, exist_ok=True)
    
    # 1. Caricamento Dati e Addestramento Random Forest Proxy
    X_train = pd.read_csv(os.path.join(processed_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(processed_dir, "y_train.csv")).values.ravel()
    X_test = pd.read_csv(os.path.join(processed_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(processed_dir, "y_test.csv")).values.ravel()
    
    print("Addestramento del Modello Interprete (Random Forest)...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    print("Inizio generazione grafici in analytics/...")
    
    # 2. GRAFICO 1: SHAP Values (Impatto positivo o negativo delle feature)
    try:
        explainer = shap.TreeExplainer(rf)
        shap_values = explainer.shap_values(X_test) # Calcolo del contributo esatto
        
        plt.figure()
        shap.summary_plot(shap_values, X_test, show=False)
        plt.title("SHAP Summary: Impatto delle Feature sullo Stress")
        plt.tight_layout()
        plt.savefig(os.path.join(analytics_dir, "shap_summary.png"), bbox_inches='tight')
        plt.close()
        print("Salvato: shap_summary.png")
    except Exception as e:
        print(f"Errore generazione SHAP plot (forse manca libreria python): {e}")

    # 3. GRAFICO 2: Actual vs Predicted Scatter Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, alpha=0.6, color='dodgerblue', edgecolor='black')
    
    # Disegno la "Diagonal of Perfection" (dove Asse X = Asse Y)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Predizione Perfetta')
    
    plt.title("Stress Reale vs Stress Calcolato dall'AI")
    plt.xlabel("Stress Reale (Ground Truth)")
    plt.ylabel("Stress Stimato (Predetto)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "actual_vs_predicted.png"))
    plt.close()
    print("Salvato: actual_vs_predicted.png")
    
    # 4. GRAFICO 3: Analisi degli Errori (Residual Plot)
    residuals = y_test - y_pred
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, bins=20, kde=True, color='crimson')
    plt.axvline(0, color='black', linestyle='--', lw=2, label='Zero Error')
    plt.title("Distribuzione dell'Errore (Residui)\n<0 Modello sovrastima, >0 Modello sottostima")
    plt.xlabel("Errore (Reale - Predetto)")
    plt.ylabel("Frequenza (Numero di Studenti)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "residual_analysis.png"))
    plt.close()
    print("Salvato: residual_analysis.png")
    
    # 5. GRAFICO 4: Coping Mechanism Impact (Isolamento Strategico)
    coping_cols = [c for c in X_train.columns if c.startswith('Coping_')]
    if len(coping_cols) > 0:
        coping_names = []
        coping_importance = []
        
        feature_importances = pd.Series(rf.feature_importances_, index=X_train.columns)
        
        idx_to_name = lambda c: c.replace('Coping_', '')
        for col in coping_cols:
            coping_names.append(idx_to_name(col))
            coping_importance.append(feature_importances[col])
            
        plt.figure(figsize=(12, 6))
        sns.barplot(x=coping_importance, y=coping_names, palette="Spectral")
        plt.title("Impatto Relativo delle Singole Strategie di Coping")
        plt.xlabel("Sensibilità Algoritmica (Information Gain)")
        plt.ylabel("Strategia di Coping")
        plt.tight_layout()
        plt.savefig(os.path.join(analytics_dir, "coping_impact.png"))
        plt.close()
        print("Salvato: coping_impact.png")
    
    print("\nTutte le visualizzazioni analitiche sono state salvate correttamente!")

if __name__ == "__main__":
    main()

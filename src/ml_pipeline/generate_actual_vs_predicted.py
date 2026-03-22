import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.ensemble import RandomForestRegressor
import warnings

warnings.filterwarnings('ignore')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "data", "processed")
    analytics_dir = os.path.join(base_dir, "analytics")
    
    X_train = pd.read_csv(os.path.join(processed_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(processed_dir, "y_train.csv")).values.ravel()
    
    features_7 = ['Work_Rest_Ratio', 'Social_Exercise_Ratio', 'Study Hours Per Week', 'Age', 
                  'Physical Exercise (Hours per week)', 'Sleep Duration (Hours per night)', 
                  'Relationship Stress']
    X_train_7 = X_train[features_7]
    
    model = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # Generazione previsioni in cross-validation
    y_pred = cross_val_predict(model, X_train_7, y_train, cv=kf, n_jobs=-1)
    
    # 1. Scatter Plot (Predetto vs Reale)
    plt.figure(figsize=(10, 8))
    sns.scatterplot(x=y_train, y=y_pred, alpha=0.5, color="#00B4D8", s=60, edgecolor="black")
    
    # Linea Perfetta (y = x)
    min_val = min(min(y_train), min(y_pred))
    max_val = max(max(y_train), max(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label="Previsione Perfetta (y=x)")
    
    plt.title("Confronto: Livello di Stress Reale vs Predetto (Nuovo RF)")
    plt.xlabel("Stress Reale (Ground Truth)")
    plt.ylabel("Stress Predetto (Modello)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "NEW_actual_vs_predicted.png"))
    plt.close()
    
    # 2. Histogram dei Residui
    residuals = y_train - y_pred
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True, color="#7209B7", bins=35)
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label="Errore Zero")
    plt.title("Distribuzione dell'Errore (Reale - Predetto)")
    plt.xlabel("Scarto (Errore)")
    plt.ylabel("Frequenza (N. di studenti)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "NEW_error_distribution.png"))
    plt.close()

    print("Success: Generated NEW_actual_vs_predicted.png and NEW_error_distribution.png")

if __name__ == "__main__":
    main()

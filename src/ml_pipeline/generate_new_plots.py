import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
import warnings

warnings.filterwarnings('ignore')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "data", "processed")
    analytics_dir = os.path.join(base_dir, "analytics")
    os.makedirs(analytics_dir, exist_ok=True)
    
    # Load data
    file_X = os.path.join(processed_dir, "X_train.csv")
    file_y = os.path.join(processed_dir, "y_train.csv")
    X_train = pd.read_csv(file_X)
    y_train = pd.read_csv(file_y).values.ravel()
    
    # Target 7 features of the NEW model
    features_7 = ['Work_Rest_Ratio', 'Social_Exercise_Ratio', 'Study Hours Per Week', 'Age', 
                  'Physical Exercise (Hours per week)', 'Sleep Duration (Hours per night)', 
                  'Relationship Stress']
    X_train_7 = X_train[features_7]
    
    # 1. Define models
    models = {
        "Vecchio Ridge (Tutte le feat)": (Ridge(alpha=1.0), X_train),
        "Nuovo Random Forest (7 feat)": (RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42), X_train_7)
    }
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    results_rmse = {}
    residuals_dict = {}
    
    print("Elaborazione Metriche e Errori Assoluti (Cross Validazione in corso...)")
    for name, (model, X_data) in models.items():
        # CV RMSE
        scores = cross_val_score(model, X_data, y_train, scoring='neg_mean_squared_error', cv=kf, n_jobs=-1)
        mean_rmse = np.sqrt(-scores).mean()
        results_rmse[name] = mean_rmse
        
        # Out-of-fold predictions
        y_pred = cross_val_predict(model, X_data, y_train, cv=kf, n_jobs=-1)
        residuals = np.abs(y_train - y_pred)
        residuals_dict[name] = residuals
        print(f"[{name}] RMSE: {mean_rmse:.4f}")
        
    # --- PLOT 1: Barplot RMSE Comparison ---
    plt.figure(figsize=(10, 6))
    sorted_res = dict(sorted(results_rmse.items(), key=lambda item: item[1], reverse=True))
    sns.barplot(x=list(sorted_res.values()), y=list(sorted_res.keys()), palette="magma")
    plt.title("Nuovo Confronto RMSE (Più basso è meglio)")
    plt.xlabel("Root Mean Squared Error (RMSE)")
    plt.xlim(2.5, max(results_rmse.values()) + 0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "NEW_rmse_comparison.png"))
    plt.close()
    
    # --- PLOT 2: Violin Plot dei Residui (Assoluti) ---
    plt.figure(figsize=(10, 6))
    res_df = pd.DataFrame(residuals_dict)
    res_df_melt = res_df.melt(var_name="Modello", value_name="Errore Assoluto (Residuo)")
    sns.violinplot(x="Errore Assoluto (Residuo)", y="Modello", data=res_df_melt, palette="muted", inner="quartile")
    plt.title("Violin Plot: Distribuzione degli Errori Assoluti")
    plt.xlabel("Distanza dallo Stress Reale (Errore)")
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "NEW_violin_residuals.png"))
    plt.close()
    
    # --- PLOT 3: Feature Importance ---
    new_rf = models["Nuovo Random Forest (7 feat)"][0]
    new_rf.fit(X_train_7, y_train)
    feat_df = pd.DataFrame({'Feature': features_7, 'Importance': new_rf.feature_importances_}).sort_values('Importance', ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=feat_df, palette="viridis")
    plt.title("Feature Importance: Nuovo Random Forest Definitivo")
    plt.xlabel("Gain (Importanza)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "NEW_feature_importance.png"))
    plt.close()
    
    # --- PLOT 4: Heatmap di Correlazione (7 Feat + Target) ---
    plt.figure(figsize=(10, 8))
    df_corr = X_train_7.copy()
    df_corr['Target_Stress'] = y_train
    sns.heatmap(df_corr.corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Heatmap Correlazioni: Le 7 Variabili d'Erosione dello Stress")
    plt.tight_layout()
    plt.savefig(os.path.join(analytics_dir, "NEW_correlation_heatmap.png"))
    plt.close()
    
    print("Generazione dei file NEW_ completata con successo nella cartella analytics!")

if __name__ == "__main__":
    main()

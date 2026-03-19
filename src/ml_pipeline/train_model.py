import os
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
import xgboost as xgb

# Disattiviamo i col_sample warnings di xgboost
warnings.filterwarnings('ignore')

def main():
    base_dir = r"c:\Users\Master\Documents\GitHub\ZenPlanner"
    processed_dir = os.path.join(base_dir, "data", "processed")
    analytics_dir = os.path.join(base_dir, "analytics")
    
    os.makedirs(analytics_dir, exist_ok=True)
    
    file_X_train = os.path.join(processed_dir, "X_train.csv")
    file_y_train = os.path.join(processed_dir, "y_train.csv")
    
    X_train = pd.read_csv(file_X_train)
    y_train = pd.read_csv(file_y_train).values.ravel()
    
    print("=== BATTAGLIA DEGLI ALGORITMI CON GRAFICI ===")
    
    models = {
        "Linear Regression (Ridge)": Ridge(alpha=1.0),
        "Support Vector Regression (SVR)": SVR(kernel='rbf', C=1.0, epsilon=0.1),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting (XGBoost)": xgb.XGBRegressor(
            n_estimators=100, 
            random_state=42, 
            objective='reg:squarederror'
        )
    }
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    
    print("Calcolo Metriche RMSE in corso...")
    best_model_name = None
    best_rmse = float('inf')
    
    for name, model in models.items():
        cv_scores = cross_val_score(model, X_train, y_train, scoring='neg_mean_squared_error', cv=kf, n_jobs=-1)
        mean_rmse = np.sqrt(-cv_scores).mean()
        results[name] = mean_rmse
        print(f"[{name}] RMSE: {mean_rmse:.4f}")
        if mean_rmse < best_rmse:
            best_rmse = mean_rmse
            best_model_name = name
        
    # 1. PLOT DEI RISULTATI RMSE
    plt.figure(figsize=(12, 6))
    # Ordinamento decrescente (il peggiore in alto, il migliore in basso)
    sorted_res = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    sns.barplot(x=list(sorted_res.values()), y=list(sorted_res.keys()), palette="magma")
    plt.title("Confronto RMSE dei Modelli (Più basso è meglio)")
    plt.xlabel("Root Mean Squared Error (RMSE)")
    plt.xlim(2.5, max(sorted_res.values()) + 0.5) # Zoom sulle variazioni
    plt.tight_layout()
    plot_rmse_path = os.path.join(analytics_dir, 'model_rmse_comparison.png')
    plt.savefig(plot_rmse_path)
    plt.close()
    
    # 2. ESTRAZIONE E PLOT DELLE FEATURE IMPORTANCES
    # Usiamo Random Forest perche' a differenza dei modelli lineari calcola
    # l'Information Gain (importanza nativa) per ogni feature sugli alberi.
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    importances = rf.feature_importances_
    
    feat_df = pd.DataFrame({
        'Feature': X_train.columns, 
        'Importance': importances
    })
    
    # Ordiniamo in modo decrescente e prendiamo le prime 15 feature
    feat_df = feat_df.sort_values(by='Importance', ascending=False).head(15)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=feat_df, x='Importance', y='Feature', palette="viridis")
    plt.title("Top 15 Feature Importanti (Nativo in Random Forest)")
    plt.xlabel("Information Gain (Importanza Relativa %)")
    plt.ylabel("")
    plt.tight_layout()
    plot_feat_path = os.path.join(analytics_dir, 'feature_importance_rf.png')
    plt.savefig(plot_feat_path)
    plt.close()
    
    print("\nSalvati i seguenti grafici analitici in analytics/:")
    print(f"- {plot_rmse_path}")
    print(f"- {plot_feat_path}")
    
    # Check manuale sull'importanza delle feature ingegnerizzate
    wr_imp = feat_df[feat_df['Feature'] == 'Work_Rest_Ratio']['Importance'].values
    se_imp = feat_df[feat_df['Feature'] == 'Social_Exercise_Ratio']['Importance'].values
    
    print("\nImpatto percentuale stimato delle feature Ratio sul modello:")
    if len(wr_imp) > 0: print(f"Work_Rest_Ratio: {wr_imp[0]*100:.2f}%")
    if len(se_imp) > 0: print(f"Social_Exercise_Ratio: {se_imp[0]*100:.2f}%")

    # 3. ESPORTAZIONE DEL MIGLIOR MODELLO PER L'ORACOLO CSP
    import joblib
    print(f"\n[ESPORTAZIONE] Il miglior modello è risultato: {best_model_name} con RMSE: {best_rmse:.4f}")
    best_algorithm = models[best_model_name]
    best_algorithm.fit(X_train, y_train)
    
    models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "tuned_best_model.pkl")
    features_path = os.path.join(models_dir, "model_features.pkl")
    
    joblib.dump(best_algorithm, model_path)
    joblib.dump(list(X_train.columns), features_path)
    print(f"Modello e Features esportati correttamente in: {models_dir}")

if __name__ == "__main__":
    main()

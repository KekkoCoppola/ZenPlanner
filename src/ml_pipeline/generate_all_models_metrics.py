import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold, cross_validate
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
import xgboost as xgb
import warnings

warnings.filterwarnings('ignore')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "data", "processed")
    analytics_dir = os.path.join(base_dir, "analytics")
    os.makedirs(analytics_dir, exist_ok=True)
    
    file_X = os.path.join(processed_dir, "X_train.csv")
    file_y = os.path.join(processed_dir, "y_train.csv")
    X_train = pd.read_csv(file_X)
    y_train = pd.read_csv(file_y).values.ravel()
    
    features_7 = ['Work_Rest_Ratio', 'Social_Exercise_Ratio', 'Study Hours Per Week', 'Age', 
                  'Physical Exercise (Hours per week)', 'Sleep Duration (Hours per night)', 
                  'Relationship Stress']
    X_train_7 = X_train[features_7]
    
    models = {
        "Old Ridge (All)": (Ridge(alpha=1.0), X_train),
        "Old SVR (All)": (SVR(kernel='rbf', C=1.0, epsilon=0.1), X_train),
        "Old Random Forest (All)": (RandomForestRegressor(n_estimators=100, random_state=42), X_train),
        "Old XGBoost (All)": (xgb.XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror'), X_train),
        "NEW Random Forest (7 feat)": (RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42), X_train_7)
    }
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    scoring = {
        'mse': 'neg_mean_squared_error',
        'mae': 'neg_mean_absolute_error',
        'r2': 'r2'
    }
    
    results = {'RMSE': {}, 'MSE': {}, 'MAE': {}, 'R2': {}}
    
    print("Calcolo metriche multiple per 5 Modelli in corso...")
    
    for name, (model, X_data) in models.items():
        cv_res = cross_validate(model, X_data, y_train, scoring=scoring, cv=kf, n_jobs=-1)
        
        mse = -cv_res['test_mse'].mean()
        rmse = np.sqrt(mse)
        mae = -cv_res['test_mae'].mean()
        r2 = cv_res['test_r2'].mean()
        
        results['MSE'][name] = mse
        results['RMSE'][name] = rmse
        results['MAE'][name] = mae
        results['R2'][name] = r2
        
        print(f"[{name}] RMSE: {rmse:.4f} | MSE: {mse:.4f} | MAE: {mae:.4f} | R2: {r2:.4f}")
        
    metrics_config = [
        ('RMSE', 'ALL_MODELS_RMSE_comparison.png', 'Root Mean Squared Error (Più basso è meglio)', True),
        ('MSE', 'ALL_MODELS_MSE_comparison.png', 'Mean Squared Error (Più basso è meglio)', True),
        ('MAE', 'ALL_MODELS_MAE_comparison.png', 'Mean Absolute Error (Più basso è meglio)', True),
        ('R2', 'ALL_MODELS_R2_comparison.png', 'R-squared (Più alto è meglio)', False)
    ]
    
    for metric_name, filename, xlabel, lower_is_better in metrics_config:
        plt.figure(figsize=(12, 6))
        
        sorted_dict = dict(sorted(results[metric_name].items(), key=lambda item: item[1], reverse=lower_is_better))
        
        sns.barplot(x=list(sorted_dict.values()), y=list(sorted_dict.keys()), palette="mako" if lower_is_better else "flare")
        plt.title(f"Confronto GLOBALE {metric_name} tra tutti i 5 Modelli")
        plt.xlabel(xlabel)
        
        # Dynamic zoom calculation per metric
        min_val = min(sorted_dict.values())
        max_val = max(sorted_dict.values())
        diff = max_val - min_val if max_val != min_val else 0.5
        
        if lower_is_better:
            plt.xlim(max(0, min_val - diff*1.5), max_val + diff*0.5)
        else:
            plt.xlim(max(0, min_val - diff*0.5), min(1.0, max_val + diff*2))
            
        plt.tight_layout()
        plt.savefig(os.path.join(analytics_dir, filename))
        plt.close()
        
    print(f"Integrazione completata! I 4 grafici ALL_MODELS sono stati generati.")

if __name__ == "__main__":
    main()

"""
Esporta il modello Random Forest e lo Scaler in formato JSON
per essere usato nella versione mobile (HTML/CSS/JS puro).
"""
import os
import json
import joblib
import numpy as np

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")

# --- Carica il modello e scaler ---
model = joblib.load(os.path.join(models_dir, "tuned_best_model.pkl"))
scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
model_features = joblib.load(os.path.join(models_dir, "model_features.pkl"))

print(f"Tipo modello: {type(model).__name__}")
print(f"Feature del modello ({len(model_features)}): {model_features}")
print(f"Feature scaler ({len(scaler.feature_names_in_)}): {list(scaler.feature_names_in_)}")

# --- Esporta lo Scaler (StandardScaler) ---
scaler_data = {
    "feature_names": list(scaler.feature_names_in_),
    "mean": scaler.mean_.tolist(),
    "scale": scaler.scale_.tolist()
}

# --- Esporta la Random Forest come struttura ad alberi ---
def export_tree(tree, feature_names):
    """Esporta un singolo Decision Tree in formato JSON ricorsivo."""
    t = tree.tree_
    
    def recurse(node_id):
        if t.children_left[node_id] == -1:  # Foglia
            # Valore foglia: media dei valori nel nodo (per regressione)
            return {"leaf": float(t.value[node_id][0][0])}
        
        feature_idx = int(t.feature[node_id])
        threshold = float(t.threshold[node_id])
        feature_name = feature_names[feature_idx]
        
        return {
            "feature": feature_name,
            "threshold": threshold,
            "left": recurse(t.children_left[node_id]),
            "right": recurse(t.children_right[node_id])
        }
    
    return recurse(0)

print(f"\nEsportazione di {model.n_estimators} alberi della Random Forest...")
trees = []
for i, estimator in enumerate(model.estimators_):
    tree_data = export_tree(estimator, model_features)
    trees.append(tree_data)
    if (i + 1) % 50 == 0:
        print(f"  Alberi esportati: {i+1}/{model.n_estimators}")

model_data = {
    "type": "RandomForestRegressor",
    "n_estimators": model.n_estimators,
    "model_features": model_features,
    "trees": trees
}

# --- Salva i JSON ---
output_dir = os.path.join(base_dir, "assets")

scaler_path = os.path.join(output_dir, "scaler.json")
model_path = os.path.join(output_dir, "model.json")

with open(scaler_path, "w") as f:
    json.dump(scaler_data, f, separators=(',', ':'))  # Minimizzato
print(f"\nScaler salvato: {scaler_path} ({os.path.getsize(scaler_path):,} bytes)")

with open(model_path, "w") as f:
    json.dump(model_data, f, separators=(',', ':'))  # Minimizzato
model_size = os.path.getsize(model_path)
print(f"Modello salvato: {model_path} ({model_size:,} bytes = {model_size/1024/1024:.2f} MB)")

# --- Verifica rapida della predizione ---
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Test con valori di esempio
test_input = {
    'Age': 22,
    'Academic Performance (GPA)': 3.0,
    'Study Hours Per Week': 20,
    'Social Media Usage (Hours per day)': 2.0,
    'Sleep Duration (Hours per night)': 7.0,
    'Physical Exercise (Hours per week)': 3,
    'Family Support': 3,
    'Financial Stress': 3,
    'Peer Pressure': 3,
    'Relationship Stress': 2,
    'Diet Quality': 3
}

work_rest_ratio = test_input['Study Hours Per Week'] / max(test_input['Sleep Duration (Hours per night)'] * 7, 1)
social_ex = (test_input['Social Media Usage (Hours per day)'] * 7) / (test_input['Physical Exercise (Hours per week)'] + 0.1)

full_input = {**test_input, 'Work_Rest_Ratio': work_rest_ratio, 'Social_Exercise_Ratio': social_ex}

df = pd.DataFrame([full_input])

# Scala con le feature del scaler
df_for_scaling = df[scaler.feature_names_in_]
df_scaled = df_for_scaling.copy()
df_scaled.loc[:, :] = scaler.transform(df_for_scaling)

# Predizione
final_input = df_scaled[model_features]
prediction = model.predict(final_input)[0]
stress = min(10.0, max(1.0, prediction))
print(f"\nVerifica predizione stress con dati di esempio: {stress:.2f}")
print("Export completato con successo!")

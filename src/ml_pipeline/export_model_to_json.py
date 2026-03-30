"""
Esporta il modello Random Forest e lo Scaler in formato JSON
per essere usato nella versione mobile (HTML/CSS/JS puro).

FIX: usa model.feature_names_in_ (7 feature reali del modello)
     invece di model_features.pkl (artefatto obsoleto con 23 feature)
"""
import os
import json
import joblib
import numpy as np
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")

# --- Carica il modello e scaler ---
model  = joblib.load(os.path.join(models_dir, "tuned_best_model.pkl"))
scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))

# CRITICO: usa model.feature_names_in_ — le feature REALI su cui il modello è stato addestrato.
# model_features.pkl è un artefatto di train_model.py (23 feature), non del retrain finale (7 feature).
model_features = list(model.feature_names_in_)

print(f"Tipo modello: {type(model).__name__}")
print(f"Feature del modello ({len(model_features)} — da model.feature_names_in_):")
print(f"  {model_features}")
print(f"Feature scaler ({len(scaler.feature_names_in_)}):")
print(f"  {list(scaler.feature_names_in_)}")

# --- Esporta lo Scaler (StandardScaler) ---
scaler_data = {
    "feature_names": list(scaler.feature_names_in_),
    "mean":  scaler.mean_.tolist(),
    "scale": scaler.scale_.tolist()
}

# --- Esporta la Random Forest come struttura ad alberi ---
def export_tree(tree, feature_names):
    t = tree.tree_
    def recurse(node_id):
        if t.children_left[node_id] == -1:
            return {"leaf": float(t.value[node_id][0][0])}
        return {
            "feature":   feature_names[int(t.feature[node_id])],
            "threshold": float(t.threshold[node_id]),
            "left":      recurse(t.children_left[node_id]),
            "right":     recurse(t.children_right[node_id])
        }
    return recurse(0)

print(f"\nEsportazione di {model.n_estimators} alberi...")
trees = []
for i, est in enumerate(model.estimators_):
    trees.append(export_tree(est, model_features))
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{model.n_estimators}")

model_data = {
    "type":            "RandomForestRegressor",
    "n_estimators":    model.n_estimators,
    "model_features":  model_features,
    "scaler_features": list(scaler.feature_names_in_),
    "trees":           trees
}

# --- Salva ---
output_dir  = os.path.join(base_dir, "assets")
scaler_path = os.path.join(output_dir, "scaler.json")
model_path  = os.path.join(output_dir, "model.json")

with open(scaler_path, "w") as f:
    json.dump(scaler_data, f, separators=(',', ':'))
print(f"\nScaler: {scaler_path} ({os.path.getsize(scaler_path):,} bytes)")

with open(model_path, "w") as f:
    json.dump(model_data, f, separators=(',', ':'))
sz = os.path.getsize(model_path)
print(f"Modello: {model_path} ({sz:,} bytes = {sz/1024/1024:.2f} MB)")

# --- Verifica parity Python vs JS-simulato ---
raw = {
    'Age': 22, 'Academic Performance (GPA)': 3.0,
    'Study Hours Per Week': 20, 'Social Media Usage (Hours per day)': 2.0,
    'Sleep Duration (Hours per night)': 7.0, 'Physical Exercise (Hours per week)': 3,
    'Family Support': 3, 'Financial Stress': 3, 'Peer Pressure': 3,
    'Relationship Stress': 2, 'Diet Quality': 3
}
raw['Work_Rest_Ratio']      = raw['Study Hours Per Week'] / max(raw['Sleep Duration (Hours per night)'] * 7, 1)
raw['Social_Exercise_Ratio']= (raw['Social Media Usage (Hours per day)'] * 7) / (raw['Physical Exercise (Hours per week)'] + 0.1)

df_sc = pd.DataFrame([raw])[list(scaler.feature_names_in_)]
scaled = pd.DataFrame(scaler.transform(df_sc), columns=scaler.feature_names_in_)

pred_py = float(model.predict(scaled[model_features])[0])
stress_py = min(10.0, max(1.0, pred_py))

def traverse(node, fvals):
    if 'leaf' in node: return node['leaf']
    return traverse(node['left'] if fvals.get(node['feature'], 0) <= node['threshold'] else node['right'], fvals)

fvals    = {c: float(scaled[c].iloc[0]) for c in model_features}
pred_js  = sum(traverse(t, fvals) for t in trees) / len(trees)
stress_js= min(10.0, max(1.0, pred_js))

print(f"\n{'='*52}")
print(f"PARITY CHECK Python sklearn vs JS simulato")
print(f"  Python:  {stress_py:.6f}")
print(f"  JS sim:  {stress_js:.6f}")
print(f"  Delta:   {abs(stress_py - stress_js):.8f}")
print(f"  OK:      {abs(stress_py - stress_js) < 1e-6}")
print(f"{'='*52}")

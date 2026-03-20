import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

base_dir = r"c:\Users\franc\Desktop\ZenPlanner"
processed_dir = os.path.join(base_dir, "data", "processed")
models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")

# Carica X_train e y_train
X_train = pd.read_csv(os.path.join(processed_dir, "X_train.csv"))
y_train = pd.read_csv(os.path.join(processed_dir, "y_train.csv")).values.ravel()

# Le feature rilevanti scoperte precedentemente
features = ['Work_Rest_Ratio', 'Social_Exercise_Ratio', 'Study Hours Per Week', 'Age', 
            'Physical Exercise (Hours per week)', 'Sleep Duration (Hours per night)', 
            'Relationship Stress']

# Prepara X_train subset
X_train_sub = X_train[features]

# Addestra una Random Forest non lineare
rf = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42)
rf.fit(X_train_sub, y_train)

# Verifica R^2 sul training per assicurarci che abbia imparato qualcosa
r2_score = rf.score(X_train_sub, y_train)
print(f"Random Forest Training R^2: {r2_score:.4f}")

# Sovrascrive il file pickel del best model
model_path = os.path.join(models_dir, "tuned_best_model.pkl")
joblib.dump(rf, model_path)
print("Nuovo modello Random Forest salvato con successo!")

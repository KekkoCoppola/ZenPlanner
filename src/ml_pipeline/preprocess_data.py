import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_path = os.path.join(base_dir, "data", "Student_Mental_Stress_and_Coping_Mechanisms.csv")
    output_dir = os.path.join(base_dir, "data", "processed")
    models_dir = os.path.join(base_dir, "src", "ml_pipeline", "models")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"Caricamento dati originali da: {input_path}")
    df = pd.read_csv(input_path)
    df.columns = df.columns.str.strip()
    
    initial_len = len(df)
    
    # 1. OUTLIER MANAGEMENT (Rimozione record anomali per proteggere lo Scaler)
    df = df[df['Study Hours Per Week'] <= 80]
    df = df[(df['Sleep Duration (Hours per night)'] >= 3) & (df['Sleep Duration (Hours per night)'] <= 14)]
    print(f"Outliers rimossi: {initial_len - len(df)} record estremi eliminati.")
    
    # 2. FEATURE ENGINEERING (Creazione di indici derivati per incrementare l'accuratezza)
    # Indice di Carico: Ore di studio a settimana diviso ore di sonno settimanali
    df['Work_Rest_Ratio'] = df['Study Hours Per Week'] / (df['Sleep Duration (Hours per night)'] * 7)
    
    # Indice di Sedentarieta' Sociale: Ore passate sui social settimanali vs Esercizio Fisico
    df['Social_Exercise_Ratio'] = (df['Social Media Usage (Hours per day)'] * 7) / (df['Physical Exercise (Hours per week)'] + 0.1) # 0.1 evita DivisionByZero
    print("Feature Engineering: create le features 'Work_Rest_Ratio' e 'Social_Exercise_Ratio'.")
    
    # 3. RIMOZIONE COLONNE INDESIDERATE E BIASI
    features_to_drop = [
        'Medical Condition', 'Family Mental Health History', 'Substance Use',
        'Counseling Attendance', 'Cognitive Distortions', 'Student ID', 'Gender'
    ]
    cols_to_drop = [c for c in features_to_drop if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    
    # 4. ENCODING CATEGORIALE
    if 'Stress Coping Mechanisms' in df.columns:
        df = pd.get_dummies(df, columns=['Stress Coping Mechanisms'], drop_first=False)
        df.columns = [col.replace('Stress Coping Mechanisms_', 'Coping_') for col in df.columns]
        coping_cols = [col for col in df.columns if col.startswith('Coping_')]
        for col in coping_cols:
            df[col] = df[col].astype(int)
            
    # Prepara Target e Features
    target_col = 'Mental Stress Level'
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # 5. DATA LEAKAGE FIX & TRAIN/TEST SPLIT
    # Dividiamo i dati PRIMA di calcolare la media e la varianza dello StandardScaler!
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Data Split completato. Train: {len(X_train)} records | Test: {len(X_test)} records.")
    
    # 6. SCALING CORRETTO (Fit solo sul Train)
    numeric_features = [
        'Age', 'Academic Performance (GPA)', 'Study Hours Per Week', 
        'Social Media Usage (Hours per day)', 'Sleep Duration (Hours per night)', 
        'Physical Exercise (Hours per week)', 'Family Support', 'Financial Stress', 
        'Peer Pressure', 'Relationship Stress', 'Diet Quality',
        'Work_Rest_Ratio', 'Social_Exercise_Ratio' # Nuove feature numeriche
    ]
    
    numeric_features = [c for c in numeric_features if c in X_train.columns]
    
    if len(numeric_features) > 0:
        scaler = StandardScaler()
        # Apprende la scala SOLTANTO dal Train Set
        X_train[numeric_features] = scaler.fit_transform(X_train[numeric_features])
        # Applica ai dati di Test in modalita' stagna (solo transform)
        X_test[numeric_features] = scaler.transform(X_test[numeric_features])
        
        # Salva lo scaler aggiornato
        scaler_path = os.path.join(models_dir, 'scaler.pkl')
        joblib.dump(scaler, scaler_path)
        print("StandardScaler fittato sul Train Set e applicato. Scaler salvato.")
    
    # Salva i dataset pronti per il training e la validazione dei modelli ML
    X_train.to_csv(os.path.join(output_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(output_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(output_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(output_dir, "y_test.csv"), index=False)
    
    print("\nEsportazione finalizzata. File ML pronti (X_train, X_test, ecc.) salvati in data/processed/")

if __name__ == "__main__":
    main()

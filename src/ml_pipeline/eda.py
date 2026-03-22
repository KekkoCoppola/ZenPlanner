import os
import sys

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("Mancano le librerie. Installale tramite pip.")
    sys.exit(1)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_path = os.path.join(base_dir, "data", "processed", "Student_Mental_Stress_and_Coping_Mechanisms_Cleaned.csv")
    analytics_dir = os.path.join(base_dir, "analytics")
    
    os.makedirs(analytics_dir, exist_ok=True)
    
    df = pd.read_csv(input_path)
    
    print("=== DATASET INFO ===")
    df.info()
    
    print("\n=== VALORI MANCANTI (MISSING VALUES) ===")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("--> Nessun valore mancante trovato.")
    
    print("\n=== ANALISI DELLE FEATURE E POSSIBILI PULIZIE ===")
    for col in df.select_dtypes(include=['object']).columns:
        unique_vals = df[col].nunique()
        print(f"[{col}] - Tipo: Categoriale (object), Valori unici: {unique_vals}")
        if unique_vals > 50:
            print(f"  -> ATTENZIONE: '{col}' ha moltissimi valori unici. Potrebbe essere un ID, testo libero o un identificativo non predittivo.")
            
    if 'Student ID' in df.columns:
        print("\n-> SUGGERIMENTO GIA' RILEVATO: 'Student ID' è chiaramente un identificativo univoco. Andrà droppato.")
    
    # Ensure there are no leading/trailing spaces in columns
    df.columns = df.columns.str.strip()
    
    if 'Mental Stress Level' in df.columns:
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if 'Mental Stress Level' in numeric_df.columns:
            corr = numeric_df.corr()
            print("\n=== CORRELAZIONE NUMERICA CON 'Mental Stress Level' ===")
            print(corr['Mental Stress Level'].sort_values(ascending=False))
            
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
            plt.title('Matrice di Correlazione tra Feature Numeriche')
            plt.tight_layout()
            plt.savefig(os.path.join(analytics_dir, 'correlation_matrix.png'))
            plt.close()
            print(f"Salvato plot: {os.path.join(analytics_dir, 'correlation_matrix.png')}")
            
        # Plot target distribution
        plt.figure(figsize=(8, 5))
        sns.histplot(df['Mental Stress Level'], bins=10, kde=True, color='teal')
        plt.title('Distribuzione del Target: Mental Stress Level')
        plt.xlabel('Mental Stress Level')
        plt.ylabel('Frequenza')
        plt.tight_layout()
        plt.savefig(os.path.join(analytics_dir, 'target_distribution.png'))
        plt.close()
        print(f"Salvato plot: {os.path.join(analytics_dir, 'target_distribution.png')}")
        
    print("\nEDA completata con successo.")

if __name__ == "__main__":
    main()

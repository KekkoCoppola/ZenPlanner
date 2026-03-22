import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_path = os.path.join(base_dir, "data", "processed", "Student_Mental_Stress_and_Coping_Mechanisms_Cleaned.csv")
    analytics_dir = os.path.join(base_dir, "analytics")
    os.makedirs(analytics_dir, exist_ok=True)
    
    df = pd.read_csv(input_path)
    
    if 'Gender' in df.columns and 'Mental Stress Level' in df.columns:
        plt.figure(figsize=(10, 6))
        # Imposto un color palette coerente, un barplot per mostrare medie e confidenza
        sns.barplot(data=df, x='Gender', y='Mental Stress Level', capsize=0.1, palette='viridis')
        plt.title('Mental Stress Level by Gender\n(Error bars indicate confidence intervals)')
        plt.xlabel('Gender')
        plt.ylabel('Mental Stress Level')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_path = os.path.join(analytics_dir, 'gender_stress_analysis.png')
        plt.savefig(plot_path)
        plt.close()
        print(f"Salvataggio grafico completato: {plot_path}")

if __name__ == "__main__":
    main()

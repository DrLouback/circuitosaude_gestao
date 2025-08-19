import pandas as pd
import hashlib
import traceback

class AtendimentosTransformer:
    def __init__(self, df: pd.DataFrame, unidade):
        try:
            self.df = df.copy()
            self.unidade = unidade
            self.transformar()
        
        except Exception as e:
            print("❌ Erro no __init__:", e)
            traceback.print_exc()
            raise
    
    def transformar(self):
        self.df['unidade'] = self.unidade
    
        self.df['Data/Hora'] = pd.to_datetime(self.df['Data/Hora'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        self.df['data'] = self.df['Data/Hora'].dt.date

        self.df['hora'] = self.df['Data/Hora'].dt.time
        self.df['mes'] = self.df['Data/Hora'].dt.month
        print(self.df.columns)
        return self.df
    
    def dataframe(self):
        return self.df
        
    
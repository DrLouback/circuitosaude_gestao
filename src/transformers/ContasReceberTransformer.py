import pandas as pd 
import os
from src.utils.date_utils import add_month_pagamento, add_month_recebimento

class ContasReceberTransformer():
    def __init__(self, df: pd.DataFrame, unity):
        self.df = df.copy()
        self.unity = unity
        self.renomear_colunas()
        self.add_unity()
        self.remove_last_line()
        self.add_column_cpf()
        self.add_month_payment()
        self.add_month_receivement()
        self.convert_collumn_value()

    def dataframe(self):
        self.df = self.df[~self.df['numero'].astype(str).str.contains("Total", na=False)]
        return self.df    
    
    def add_unity(self):
        self.df['unidade'] = self.unity
        
    def remove_last_line(self):
        return self.df[:-1]

    def add_column_cpf(self):
       
        self.df['cpf'] = self.df['cliente'].str.split('|').str[1]
        self.df['cliente'] = self.df['cliente'].str.split('|').str[0]
        self.df['cpf'] = self.df['cpf'].str.split(':').str[1]
        return self.df
    
    def add_month_payment(self):
        return add_month_pagamento(self.df)
    
    def add_month_receivement(self):
        return add_month_recebimento(self.df)
    
    def convert_collumn_value(self):
        
        self.df['valor'] = self.df['valor'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        # Converter para float
        self.df['valor'] = pd.to_numeric(self.df['valor'], errors='coerce')
        return self.df
    
    def renomear_colunas(self):
        self.df.columns = ['index','numero','cliente','centro_de_custo','forma','cod_transacao','data_vencimento',
                    'data_pagamento','data_recebimento','situacao','valor']
    

    



if __name__ == '__main__':
    pass
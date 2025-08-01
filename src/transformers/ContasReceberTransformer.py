import pandas as pd 
import os
from src.utils.date_utils import add_month_pagamento, add_month_recebimento
import numpy as np

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
        self.extrair_telefone()
        self.limpar_nome_cliente()
        self.add_id_conta_recer()

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
    

    def extrair_telefone(self):
        self.df['telefone'] = np.where(
        self.df['cliente'].str.contains('Tel'),
        self.df['cliente'].str.split(':').str[1].str.split('Dados').str[0],
            ''
        )
        self.df['telefone'] = self.df['telefone'].apply(lambda x: str(x).replace('(','').replace(')','').replace('-','').replace(' ','').strip())
        return self.df

    def limpar_nome_cliente(self):
        self.df['cliente'] = np.where(
        self.df['cliente'].str.contains('Tel'),
        self.df['cliente'].str.split(':').str[0],
        self.df['cliente'].str.split('Dados').str[0]
        )
        self.df['cliente'] = self.df['cliente'].apply(lambda x: str(x).replace('Tel.','').strip())
        return self.df

    def add_id_conta_recer(self):
        self.df['id_conta_receber'] = self.df['numero'].astype(str) + self.df['unidade'].astype(str)

if __name__ == '__main__':
    pass
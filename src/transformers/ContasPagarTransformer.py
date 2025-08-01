import pandas as pd
from src.utils.date_utils import add_month_pagamento

class ContasPagarTransformer:
    def __init__(self, df: pd.DataFrame, unidade):
        self.df = df.copy()
        self.unidade = unidade
        self.renomear_colunas()
        self.formatar_datas()
        self.add_unidade()
        self.remove_last_line()
        self.add_month_payment()
        self.convert_collumn_value()
        self.add_id_conta_pagar()

    def dataframe(self):
        self.df = self.df[~self.df['numero'].astype(str).str.contains("Total", na=False)]
        return self.df

    def add_unidade(self):
        self.df['unidade'] = self.unidade

    def remove_last_line(self):
        self.df = self.df[:-1]

    def add_month_payment(self):
        self.df = add_month_pagamento(self.df)
        return self.df

    def convert_collumn_value(self):
        # Supondo que a coluna valor pode vir como string com ponto e vírgula
        self.df['valor'] = self.df['valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        self.df['valor'] = pd.to_numeric(self.df['valor'], errors='coerce')
        return self.df

    def renomear_colunas(self):
        self.df.columns = [
            'index', 'numero', 'fornecedor', 'titulo', 'centro_de_custo',
            'forma', 'categoria', 'data_vencimento', 'data_pagamento',
            'situacao', 'valor'
        ]

    def formatar_datas(self):
        # Formata as colunas de data para o formato correto (dayfirst=True)
        for col in ['data_vencimento', 'data_pagamento']:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce', dayfirst=True)

    def add_id_conta_pagar(self):
        self.df['id_conta_pagar'] = self.df['numero'].astype(str) + self.df['unidade'].astype(str)

if __name__ == '__main__':
    pass
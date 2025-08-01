import pandas as pd

class StoneTransformer:
    def __init__(self, df: pd.DataFrame, unidade):
        self.df =  df.drop('DESCONTO UNIFICADO', axis=1) if 'DESCONTO UNIFICADO' in df.columns else df
        self.df.columns = [col.upper().strip() for col in self.df.columns]  # Padroniza para maiúsculas
        self.renomear_colunas()  # Renomeia para nomes internos
        self.unidade = unidade
        self.add_unidade()
        self.remove_last_line()
        self.formatar_datas()
        self.add_month_venda()
        self.add_month_vencimento()
        self.convert_colunas_valor()
        self.add_id_stone_unidade()

    def dataframe(self):
        
        return self.df

    def add_unidade(self):
        self.df['unidade'] = self.unidade

    def remove_last_line(self):
        self.df = self.df[:-1]

    def formatar_datas(self):
        for col in [
            'data_venda', 'data_vencimento', 
            'vencimento_original', 'data_status'
        ]:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce', dayfirst=True)

    def add_month_venda(self):
        if 'data_venda' in self.df.columns:
            self.df['mes_venda'] = self.df['data_venda'].dt.month

    def add_month_vencimento(self):
        if 'data_vencimento' in self.df.columns:
            self.df['mes_vencimento'] = self.df['data_vencimento'].dt.month

    def convert_colunas_valor(self):
        for col in [
            'valor_bruto', 'valor_liquido', 
            'desconto', 'antecipacao'
        ]:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col]
                    .astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                )
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        for col in ['qntd_parcelas', 'parcela']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def renomear_colunas(self):
        # Renomeia as 20 colunas do arquivo para nomes internos
        
        self.df.columns = [
            'documento', 'stonecode', 'fantasia', 'categoria',
            'data_venda', 'data_vencimento', 'vencimento_original', 'bandeira',
            'produto', 'stone_id', 'qntd_parcelas', 'parcela', 'valor_bruto',
            'valor_liquido', 'desconto','antecipacao', 'cartao', 'status',
            'data_status', 'chave'
        ]

     

    def add_id_stone_unidade(self):
        self.df['id_stone_unidade'] = self.df['stone_id'].astype(str) + self.df['unidade']

if __name__ == '__main__':
    pass
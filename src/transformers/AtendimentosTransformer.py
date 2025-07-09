import pandas as pd

class AtendimentosTransformer:
    def __init__(self, df: pd.DataFrame, unidade):
        self.df = df.copy()
        self.unidade = unidade
        self.remove_last_line()
        self.add_unidade()
        self.extrair_data_de_data_hora()     
        self.formatar_datas()
        self.renomear_colunas()  

    def dataframe(self):
        return self.df

    def add_unidade(self):
        self.df['unidade'] = self.unidade

    def remove_last_line(self):
        self.df = self.df[:-1]

    def renomear_colunas(self):
        self.df.columns = [
            'index', 'cliente', 'profissional', 'data_hora', 'atendimento',
            'status', 'obs', 'unidade', 'data'
        ]

    def formatar_datas(self):
        # Formata as colunas de data para o formato correto (dayfirst=True)
        for col in ['Data/Hora', 'data']:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce', dayfirst=True)

    def extrair_data_de_data_hora(self):
        # Cria/atualiza a coluna 'data' extraindo apenas a data de 'data_hora'
        self.df['data'] = pd.to_datetime(self.df['Data/Hora'], errors='coerce', dayfirst=True).dt.date
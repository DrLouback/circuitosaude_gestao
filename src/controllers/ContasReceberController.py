from src.models.ContasReceber import ContasReceber
import pandas as pd
import streamlit as st
from src.db.db import engine
import numpy as np
from datetime import datetime

def carregar_contas_abertas():
    return pd.read_sql_query("SELECT * FROM contas_receber WHERE situacao = 'Aberta'", engine)


def filtrar_vencidas(df):
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
    hoje = datetime.now()
    return df[
        (df['data_vencimento'] <= hoje) &
        (df['data_vencimento'].dt.month == 7)&
        (df['valor'] > 0 )
    ]

def limpar_data(df: pd.DataFrame):
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce').dt.date
    return df

def gerar_json_devedores(df: pd.DataFrame):
    # Cria a mensagem personalizada para cada linha
    devedores_agrupados = df.groupby(['cliente','centro_de_custo', 'situacao', 'valor','unidade','telefone'])['valor'].sum().reset_index(name='total')
    devedores_agrupados['msg'] = devedores_agrupados.apply(
        lambda row: f"Olá {row['cliente']}, sua fatura de {row['centro_de_custo']} no valor de R$ {row['total']:.2f} está como {row['situacao']}. Unidade: {row['unidade']}.", axis=1
    )
    devedores_agrupados['msg2'] = f""" 1 - Quero realizar o pagamento. Como faço?\n2 - Já quitei essa cobrança, pode conferir por favor? """
    
    return devedores_agrupados.to_dict(orient='records')

def gerar_devedores_json():
    df = carregar_contas_abertas()
    
    df = filtrar_vencidas(df)
    df= limpar_data(df)
    return gerar_json_devedores(df)


    



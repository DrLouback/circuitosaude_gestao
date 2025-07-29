from src.models.ContasReceber import ContasReceber
import pandas as pd
import streamlit as st
from src.db.db import engine
import numpy as np
import datetime


def carregar_atendimentos():
    tipos_atendimento = ['Pilates Experimental', "Avaliação", "Fisioterapia G.D.S", "Fisioterapia ATM",
                         "Fisioterapia Pélvica", "Fisioterapia Pélvica Avaliação", "Fisioterapia R.P.G",
                         "Fisioterapia Sessão", "Fisioterapia Vestibular", "Massagem",
                         "Massagem modeladora", "Pedras quentes"]
    hoje = datetime.datetime(year=2025, month=6, day=5)
    base_query = f"SELECT * FROM atendimentos WHERE DATE(data_hora) = '{hoje}'"
    if tipos_atendimento:
        tipos_str = ','.join([f"'{tipo}'" for tipo in tipos_atendimento])
        base_query += f" AND atendimento IN ({tipos_str})"
    return pd.read_sql_query(base_query, engine)

def gerar_json_atendimentos(df):
    """
    Gera um JSON com cliente, profissional, atendimento, data, hora, unidade e mensagem personalizada.
    """
    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
    df['data_atendimento'] = df['data_hora'].dt.date.astype(str)
    df['hora_atendimento'] = df['data_hora'].dt.strftime('%H:%M')
    df_json = df[['cliente', 'profissional', 'atendimento', 'data_atendimento', 'hora_atendimento', 'unidade']].copy()
    df_json['mensagem'] = df_json.apply(
        lambda row: f"Olá {row['cliente']}, lembrando do seu atendimento de {row['atendimento']} com {row['profissional']} em {row['data_atendimento']} às {row['hora_atendimento']} na unidade {row['unidade']}.", axis=1
    )
    return df_json.to_dict(orient='records')

def atendimentos_json():
    df = carregar_atendimentos()
    return gerar_json_atendimentos(df)
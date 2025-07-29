from src.controllers.ContasReceberController import gerar_devedores_json
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
URL_POST_DEVEDORES = os.getenv(f"URL_POST_DEVEDORES")
devedores_json =  gerar_devedores_json()

devedores_df = pd.DataFrame(devedores_json)
df = devedores_df[['cliente', 'centro_de_custo','data_vencimento', 'situacao', 'valor','unidade']]
df.columns = ['Cliente', 'Centro de Custo','Data de vencimento', 'Situação', 'Valor','Unidade']
st.dataframe(df)

url = "https://new-backend.botconversa.com.br/api/v1/webhooks-automation/catch/150933/cyXyyM5y4gQ0/"

df_teste = pd.DataFrame([{
    'cliente': 'Mateus',
    'centro_de_custo': 'Fisioterapia',
    'data_vencimento': '2025-07-31 00:00:00',
    'situacao': 'Aberta',
    'valor': 240.0,
    'unidade': 'MOK',
    'telefone': '21997462608',
    'msg': f"""Olá Mateus, sua fatura de Fisioterapia no valor de R$ 240.00 está como Aberta. Unidade: MOK.""",
    'msg2': f""" 1 - Quero realizar o pagamento. Como faço?\n2 - Já quitei essa cobrança, pode conferir por favor? """
}])


test = df_teste.to_dict(orient="records")

bt_enviar = st.button('Enviar mensagem automática')
if bt_enviar:
    for i in devedores_json:
        requests.post(f'{URL_POST_DEVEDORES}', i)

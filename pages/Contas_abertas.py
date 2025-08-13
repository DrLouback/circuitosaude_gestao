from src.controllers.ContasReceberController import gerar_devedores_json
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os
import datetime
from src.db.db import engine

load_dotenv()
#URL_POST_DEVEDORES = os.getenv(f"URL_POST_DEVEDORES")
devedores_json =  gerar_devedores_json()

devedores_df = pd.DataFrame(devedores_json)

st.dataframe(devedores_df)

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

bt_enviar = st.button('Enviar cobranças MOK')
if bt_enviar:

    try:
        for i in devedores_json:
        #requests.post(f'{URL_POST_DEVEDORES}', i)
            if i['unidade'] == 'MOK':
                print('Post para MOK url', i)

        df = pd.DataFrame({
        "data_envio": [datetime.datetime.now()],
        "unidade":[ "MOK"],
        "status": [True],
        "erro": [None]
        })
        df.to_sql("log_envio_mensagem", con=engine, if_exists="append", index=False)

    except Exception as e:
            df = pd.DataFrame({
            "data_envio": [datetime.datetime.now()],
            "unidade": ["MOK"],
            "status": [False],
            "erro": [str(e)]
            })
            df.to_sql("log_envio_mensagem", con=engine, if_exists="append", index=False)
            raise Exception('Erro ao enviar mensagem: Unidade MOK')
    
log = pd.read_sql('Select * from log_envio_mensagem order by data_envio desc limit 1', engine)
if log['status'].iloc[0] == True:
    data_envio = pd.to_datetime(log["data_envio"].iloc[0])
    st.success(f'Último envio realizado em: {data_envio.strftime("%d/%m/%Y às %H:%M")}')
     
        

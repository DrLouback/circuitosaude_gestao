import pandas as pd
import streamlit as st
from src.db.db import engine
import numpy as np

unidade = st.selectbox("Unidade", ['MOK','Shopping'])


contas = pd.read_sql(f"Select * from contas_receber where situacao = 'Paga' AND unidade = '{unidade}'", engine)
stone = pd.read_sql(f"Select * from stone where unidade = '{unidade}'", engine)
contas.rename(columns={'cod_transacao':'stone_id'},inplace= True)
stone['stone_id'] = stone['stone_id'].apply(lambda x: str(x).replace(".0", ''))
#st.dataframe(contas)
#st.dataframe(stone)


st.title('Conciliados')
conciliados = pd.merge(stone, contas, on= 'stone_id').fillna('')
conciliados['Conf. Valor'] = np.where(conciliados['valor_bruto'] == conciliados['valor'], "✅", "❌")

conciliados['Conf. Data'] = np.where(pd.to_datetime(conciliados['data_venda']).dt.date == pd.to_datetime(conciliados['data_pagamento']).dt.date, "✅", "❌")

resumo_conciliados = conciliados[['cartao','stone_id','cliente','cpf','forma','valor_bruto','valor','Conf. Valor', "data_venda","data_pagamento","Conf. Data"]]


st.dataframe(resumo_conciliados)

valor_stone_conciliado = conciliados['valor_bruto'].sum()
valor_seufisio_conciliado = conciliados['valor'].sum()

st.write(f'Valor conciliado SeuFisio: R$ {valor_seufisio_conciliado:.2f}') 
st.write(f'Valor conciliado Stone: R$ {valor_stone_conciliado:.2f}')

st.write(f'Diferença: R$ {valor_seufisio_conciliado - valor_stone_conciliado:.2f}')


st.divider()
nao_conciliados = pd.merge(stone, contas, on= 'stone_id', how='outer')
st.title('Não conciliados')

nao_conciliados = nao_conciliados[nao_conciliados['cliente'].isnull()]  
nao_conciliados['Conf. Valor'] = np.where(nao_conciliados['valor_bruto'] == nao_conciliados['valor'], "✅", "❌")

nao_conciliados['Conf. Data'] = np.where(pd.to_datetime(nao_conciliados['data_venda']).dt.date == pd.to_datetime(nao_conciliados['data_pagamento']).dt.date, "✅", "❌")
nao_conciliados['Cartão já utilizado'] = np.where(
    nao_conciliados['cartao'].isin(conciliados['cartao']),
    "✅",
    "❌"
)

resumo_nao_conciliado = nao_conciliados[['cartao','stone_id','cliente','cpf','forma','valor_bruto','valor','Conf. Valor', "data_venda","data_pagamento","Conf. Data",'Cartão já utilizado']].copy()
st.dataframe(resumo_nao_conciliado.fillna('').drop_duplicates())

valor_stone_nao_conciliado = nao_conciliados['valor_bruto'].sum()
valor_seufisio_nao_conciliado = nao_conciliados['valor'].sum()

st.write(f'Valor não conciliado SeuFisio: R$ {valor_seufisio_nao_conciliado:.2f}') 
st.write(f'Valor não conciliado Stone: R$ {valor_stone_nao_conciliado:.2f}')

st.write(f'Diferença: R$ {valor_seufisio_nao_conciliado - valor_stone_nao_conciliado:.2f}')

st.divider()
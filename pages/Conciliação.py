import pandas as pd
import streamlit as st
from src.db.db import engine
import numpy as np
from io import BytesIO

unidade = st.selectbox("Unidade", ['MOK','Shopping'])
mes = st.selectbox('Mes', [4,5,6,7,8,9,10,11,12])


conciliados = pd.read_sql_query("""with stone_limpo as (SELECT id, documento, stonecode, fantasia, categoria, data_venda, data_vencimento, vencimento_original, bandeira, produto, REGEXP_REPLACE(stone_id, '\\.0$', '') AS stone_id, qntd_parcelas, parcela, valor_bruto, valor_liquido, desconto, antecipacao, cartao, status, data_status, chave, unidade, mes_venda, mes_vencimento, id_stone_unidade
	FROM public.stone)
	SELECT
         b.cartao, 
        b.stone_id,
		a.unidade as unidade_seufisio,
        a.cliente,
        a.cpf,
		b.data_venda as data_stone,
		a.data_pagamento as data_seufisio,
        b.produto,
		b.valor_bruto as valor_stone,
		a.valor as valor_seufisio,
		b.valor_liquido
	FROM stone_limpo b
	left join contas_receber a
	on b.stone_id = a.cod_transacao
	where a.cod_transacao is not null;
	""", engine)


conciliados['Conf. Valor'] = np.where(conciliados['valor_stone'] == conciliados['valor_seufisio'], "✅", "❌")

conciliados['Conf. Data'] = np.where(pd.to_datetime(conciliados['data_stone']).dt.date == pd.to_datetime(conciliados['data_seufisio']).dt.date, "✅", "❌")

nao_conciliado_seufisio = pd.read_sql_query("""WITH stone_limpo AS (
  SELECT 
    REGEXP_REPLACE(stone_id, '\\.0$', '') AS stone_id
  FROM public.stone
)

select a.stone_id as id_stone,
b.cod_transacao as id_seufisio,
b.valor,
b.cliente,
b.data_pagamento as "data pagamento no SeuFisio",
b.forma,
b.unidade
from stone_limpo a
right join contas_receber b
on a.stone_id = b.cod_transacao 
where a.stone_id is null
and b.forma in ('Cartão de crédito','Cartão de débito');
 """, engine)


nao_conciliados_stone = pd.read_sql_query("""with stone_limpo as (SELECT id, documento, stonecode, fantasia, categoria, data_venda, data_vencimento, vencimento_original, bandeira, produto, REGEXP_REPLACE(stone_id, '\\.0$', '') AS stone_id, qntd_parcelas, parcela, valor_bruto, valor_liquido, desconto, antecipacao, cartao, status, data_status, chave, unidade, mes_venda, mes_vencimento, id_stone_unidade
	FROM public.stone)
	SELECT
         b.cartao, 
        b.stone_id,
		b.unidade as unidade,
		b.data_venda as data_stone,
		b.produto,
		b.valor_bruto as valor_stone,
		b.valor_liquido
	FROM stone_limpo b
	left join contas_receber a
	on b.stone_id = a.cod_transacao
	where a.cod_transacao is null;
	""", engine)

nao_conciliados_stone['Cartão já utilizado'] = np.where(
    nao_conciliados_stone['cartao'].isin(conciliados['cartao']),
    "✅",
    "❌"
)

conciliados = conciliados[conciliados['unidade_seufisio'] == f'{unidade}']
nao_conciliado_seufisio = nao_conciliado_seufisio[nao_conciliado_seufisio['unidade'] == f'{unidade}']
nao_conciliados_stone = nao_conciliados_stone[nao_conciliados_stone['unidade'] == f'{unidade}']

conciliados['mes'] = pd.to_datetime(conciliados['data_stone']).dt.month
conciliados = conciliados[conciliados['mes'] == mes]

nao_conciliado_seufisio['mes'] = pd.to_datetime(nao_conciliado_seufisio['data pagamento no SeuFisio']).dt.month
nao_conciliado_seufisio = nao_conciliado_seufisio[nao_conciliado_seufisio['mes'] == mes]

nao_conciliados_stone['mes'] = pd.to_datetime(nao_conciliados_stone['data_stone']).dt.month
nao_conciliados_stone = nao_conciliados_stone[nao_conciliados_stone['mes'] == mes]

@st.cache_data
def converter_xlsx(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def baixar_arquivo(df, mes):
    df = converter_xlsx(df)
    st.download_button("Download", data= df, file_name=f'Conciliados_{mes}.xlsx')

 #type: ignore

st.title("Pagamentos Concilidados")
st.dataframe(conciliados)
if unidade is not None:
    baixar_arquivo(conciliados, mes)

st.header('Pagamentos do SeuFisio não encontrados na Stone')
st.dataframe(nao_conciliado_seufisio)


st.header('Pagamentos da Stone não encontrados no SeuFisio')
st.dataframe(nao_conciliados_stone)

st.divider()
st.write(f"Total conciliado: {conciliados['valor_seufisio'].sum():.2f}")
st.write(f'Do SeuFisio faltam {nao_conciliado_seufisio['valor'].sum():.2f}')
st.write(f'Da Stone faltam {nao_conciliados_stone['valor_stone'].sum():.2f}')
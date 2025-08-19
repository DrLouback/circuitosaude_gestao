import pandas as pd
import streamlit as st
from src.db.db import engine
import numpy as np
from io import BytesIO

unidade = st.selectbox("Unidade", ['MOK','Shopping'])
mes = st.selectbox('Mes', [4,5,6,7,8,9,10,11,12])


conciliados = pd.read_sql_query(f"""with stone_limpo as (SELECT id, documento, stonecode, fantasia, categoria, data_venda, data_vencimento, vencimento_original, bandeira, produto, REGEXP_REPLACE(stone_id, '\\.0$', '') AS stone_id_m, qntd_parcelas, parcela, valor_bruto, valor_liquido, desconto, antecipacao, cartao, status, data_status, chave, unidade, mes_venda, mes_vencimento, id_stone_unidade
	FROM public.stone)
	SELECT 
	a.cartao, 
	REGEXP_REPLACE(a.stone_id_m, '\\.0$','') AS stone_id,
	b.cod_transacao,
	b.cliente,
	b.valor as valor_seufisio,
	a.valor_bruto as valor_stone,
	a.valor_liquido as valor_liquido,
	a.data_venda as data_stone,
	b.data_pagamento as data_seufisio from
	stone_limpo a
	left join contas_receber b
	on REGEXP_REPLACE(a.stone_id_m, '\\.0$', '') = b.cod_transacao
	where a.mes_vencimento = {mes}
	and a.unidade = '{unidade}'
    and cod_transacao is not null;""", engine)


conciliados['Conf. Valor'] = np.where(conciliados['valor_stone'] == conciliados['valor_seufisio'], "✅", "❌")

conciliados['Conf. Data'] = np.where(pd.to_datetime(conciliados['data_stone']).dt.date == pd.to_datetime(conciliados['data_seufisio']).dt.date, "✅", "❌")

nao_conciliado_seufisio = pd.read_sql_query(f"""with stone_limpo as (SELECT id, documento, stonecode, fantasia, categoria, data_venda, data_vencimento, vencimento_original, bandeira, produto, REGEXP_REPLACE(stone_id, '\\.0$', '') AS stone_id_m, qntd_parcelas, parcela, valor_bruto, valor_liquido, desconto, antecipacao, cartao, status, data_status, chave, unidade, mes_venda, mes_vencimento, id_stone_unidade
	FROM public.stone),
conciliados as(	SELECT 
	a.cartao, 
	REGEXP_REPLACE(a.stone_id_m, '\\.0$','') AS stone_id,
	b.cod_transacao,
	b.cliente,
	b.forma,
	b.valor as valor_seufisio,
	a.valor_bruto as valor_stone,
	a.valor_liquido as valor_liquido,
	a.data_venda,
	b.data_pagamento,
    b.mes_pagamento,
    b.unidade from
	stone_limpo a
	right join contas_receber b
	on REGEXP_REPLACE(a.stone_id_m, '\\.0$', '') = b.cod_transacao
	where b.forma in ('Cartão de crédito', 'Cartão de débito')
	)
	
select *  from conciliados where stone_id is null 
and mes_pagamento = {mes}
	and unidade = '{unidade}'""", engine)


nao_conciliados_stone = pd.read_sql_query(f"""with stone_limpo as (SELECT id, documento, stonecode, fantasia, categoria, data_venda, data_vencimento, vencimento_original, bandeira, produto, REGEXP_REPLACE(stone_id, '\\.0$', '') AS stone_id_m, qntd_parcelas, parcela, valor_bruto, valor_liquido, desconto, antecipacao, cartao, status, data_status, chave, unidade, mes_venda, mes_vencimento, id_stone_unidade
	FROM public.stone)
	SELECT 
	a.cartao, 
	REGEXP_REPLACE(a.stone_id_m, '\\.0$','') AS stone_id,
	b.cod_transacao,
	b.cliente,
	b.valor as valor_seufisio,
	a.valor_bruto as valor_stone,
	a.valor_liquido as valor_liquido,
	a.data_venda as data_stone,
	b.data_pagamento as data_seufisio from
	stone_limpo a
	left join contas_receber b
	on REGEXP_REPLACE(a.stone_id_m, '\\.0$', '') = b.cod_transacao
	where a.mes_vencimento = {mes}
	and a.unidade = '{unidade}'
    and cod_transacao is null;""", engine)

nao_conciliados_stone['Cartão já utilizado'] = np.where(
    nao_conciliados_stone['cartao'].isin(conciliados['cartao']),
    "✅",
    "❌"
)



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
st.write(f'Do SeuFisio faltam {nao_conciliado_seufisio['valor_seufisio'].sum():.2f}')
st.write(f'Da Stone faltam {nao_conciliados_stone['valor_stone'].sum():.2f}')
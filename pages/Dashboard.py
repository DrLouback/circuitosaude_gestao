import streamlit as st
import pandas as pd
import numpy as np
from src.db.db import engine


# ------------------------------
# Seleção da unidade
# ------------------------------
unidade = st.selectbox("Selecione unidade", ['MOK', 'Shopping'])

# ------------------------------
# Leitura de dados
# ------------------------------
stone = pd.read_sql(f"SELECT * FROM stone WHERE unidade = '{unidade}'", engine)
contas_receber = pd.read_sql(f"SELECT * FROM contas_receber WHERE unidade = '{unidade}'", engine)

# ------------------------------
# Filtro de meses
# ------------------------------
meses = ['Sem filtro']
meses_unicos = contas_receber['mes_pagamento'].dropna().unique()
meses += sorted([str(int(m)) for m in meses_unicos if pd.notnull(m)])
# mes = st.selectbox('Mês', meses)

# ------------------------------
# Separação de contas pagas e abertas
# ------------------------------
contas_pagas = contas_receber[contas_receber['situacao'] == 'Paga']
contas_abertas = contas_receber[contas_receber['situacao'] == 'Aberta']

# ------------------------------
# Cartões e pagamentos SeuFisio
# ------------------------------
cartoes_stone = stone[['data_venda', 'data_vencimento', 'valor_bruto']]
pagamentos_seufisio = contas_pagas[
    ~contas_pagas['forma'].isin(['Cartão de crédito', 'Cartão de débito'])
]

# ------------------------------
# RECEBIMENTOS
# ------------------------------
contas_receber['mes_pagamento'] = contas_receber['mes_pagamento'].dropna().astype(int)

pivot_recebimentos = pagamentos_seufisio.pivot_table(
    index=[],
    columns='mes_recebimento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)
pivot_recebimentos.index = pd.Index(['Recebido'])

pivot_stone = stone.pivot_table(
    index=[],
    columns='mes_vencimento',
    values='valor_liquido',
    aggfunc='sum',
    fill_value=0
)
pivot_stone.rename(columns={'valor_liquido': 'valor', 'mes_vencimento': 'mes_pagamento'})
pivot_stone.index = pd.Index(['Recebido'])

concat_stone_seufisio = pivot_stone + pivot_recebimentos

# ------------------------------
# ALUNOS
# ------------------------------
alunos = pd.read_sql_query(f""" SELECT UPPER(TRIM(unaccent(cliente)))  AS clientes,
           *,
           EXTRACT(MONTH FROM data_vencimento) AS mes
    FROM contas_receber
    where unidade = '{unidade}'""", engine)
pivot_alunos = alunos.groupby('mes')['cliente'].nunique().reset_index()
pivot_alunos = pivot_alunos.set_index('mes').T
pivot_alunos.index = pd.Index(['Quantidade de alunos'])

st.write('Quantidade de alunos')
st.dataframe(pivot_alunos)

# ------------------------------
# CONTAS A PAGAR
# ------------------------------
st.divider()
contas_pagar = pd.read_sql(f"SELECT * FROM contas_pagar WHERE unidade = '{unidade}'", engine)
contas_pagar['titulo'] = contas_pagar['titulo'].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
contas_pagar['mes_pagamento'] = contas_pagar['mes_pagamento'].dropna().astype(int)

pivot_contas_pagar = contas_pagar.pivot_table(
    index=[],
    columns='mes_pagamento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)

# ------------------------------
# FLUXO CONSOLIDADO
# ------------------------------
todos_meses = sorted(set(pivot_recebimentos.columns).union(set(pivot_contas_pagar.columns)))
pivot_recebimentos = concat_stone_seufisio.reindex(columns=todos_meses, fill_value=0)
pivot_contas_pagar = pivot_contas_pagar.reindex(columns=todos_meses, fill_value=0)

lucro = pivot_recebimentos.values - pivot_contas_pagar.values

df_fluxo = pd.DataFrame(
    data=np.vstack([concat_stone_seufisio.values, pivot_contas_pagar.values, lucro]),
    index=['Recebido', 'Saídas', 'Lucro'],
    columns=todos_meses
)
df_fluxo['Total'] = df_fluxo.sum(axis=1)

st.write('Fluxo Real de Entradas por mês')
st.dataframe(df_fluxo)

# ------------------------------
# DIFERENÇA PERCENTUAL MÊS A MÊS
# ------------------------------
df_percent = df_fluxo.iloc[:, :-1].pct_change(axis=1) * 100
df_percent = df_percent.round(2)
df_percent.index = pd.Index([f"{idx} (%)" for idx in df_fluxo.index])

# ------------------------------
# GASTOS POR TÍTULO
# ------------------------------
pivot_titulos = contas_pagar.pivot_table(
    index='titulo',
    columns='mes_pagamento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)
pivot_titulos['Total'] = pivot_titulos.sum(axis=1)
pivot_titulos.loc['Total'] = pivot_titulos.sum(axis=0)

# ------------------------------
# DIFERENÇA ABSOLUTA DE GASTOS
# ------------------------------
pivot_titulos_diff = pivot_titulos.drop('Total', errors='ignore').iloc[:, :-1].diff(axis=1).fillna(0)
pivot_titulos_diff.loc['Total'] = pivot_titulos_diff.sum(axis=0)

st.write('Diferença absoluta de gastos por título e mês (mês atual - mês anterior)')
st.dataframe(pivot_titulos_diff)


# ------------------------------
# Faturamentos
# ------------------------------
contas_receber['mes_pagamento'] = contas_receber['mes_pagamento'].dropna().astype(int)

pivot_faturamentos = pagamentos_seufisio.pivot_table(
    index=[],
    columns='mes_pagamento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)
pivot_faturamentos.index = pd.Index(['Recebido'])

pivot_stone = stone.pivot_table(
    index=[],
    columns='mes_venda',
    values='valor_liquido',
    aggfunc='sum',
    fill_value=0
)
pivot_stone.rename(columns={'valor_liquido': 'valor', 'mes_vencimento': 'mes_pagamento'})
pivot_stone.index = pd.Index(['Recebido'])

faturamento = pivot_stone + pivot_faturamentos

# ------------------------------
# FATURAMENTO CONSOLIDADO
# ------------------------------
todos_meses = sorted(set(pivot_faturamentos.columns).union(set(pivot_contas_pagar.columns)))
pivot_faturamentos = faturamento.reindex(columns=todos_meses, fill_value=0)
pivot_contas_pagar = pivot_contas_pagar.reindex(columns=todos_meses, fill_value=0)

lucro = pivot_faturamentos.values - pivot_contas_pagar.values

df_faturamento = pd.DataFrame(
    data=np.vstack([pivot_faturamentos.values, pivot_contas_pagar.values, lucro]),
    index=['Recebido', 'Saídas', 'Lucro'],
    columns=todos_meses
)
df_faturamento['Total'] = df_faturamento.sum(axis=1)

st.write('Faturamento')
st.dataframe(df_faturamento)

print("Alunos por mês considerando alunos pagantes")
print(pivot_alunos)
print("Fluxo considerando entradas como mês que entrou dinheiro na conta")
print(df_fluxo)
print("Faturamento considerando entradas como mês de venda")
print(df_faturamento)
print("Diferença de gastos por títulos em relação ao mês anterior")
print(pivot_titulos_diff)


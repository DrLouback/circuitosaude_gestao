import streamlit as st
import pandas as pd
from src.db.db import engine
import numpy as np


unidade = st.selectbox("Selecione unidade", ['MOK','Shopping'])
contas_receber = pd.read_sql(f"Select * from contas_receber  where unidade = '{unidade}'", engine)
meses = ['Sem filtro']
meses_unicos = contas_receber['mes_pagamento'].dropna().unique()
meses += sorted([str(int(m)) for m in meses_unicos if pd.notnull(m)])

#mes = st.selectbox('Mês', meses)


contas_pagas = contas_receber[contas_receber['situacao'] == 'Paga']
contas_abertas = contas_receber[contas_receber['situacao'] == 'Aberta']
#
#if mes != "Sem filtro":
#    contas_pagas = contas_receber[(contas_receber['situacao'] == 'Paga') & 
#                                  (contas_receber['mes_pagamento'] == int(mes))]
#    
#    contas_abertas = contas_receber[(contas_receber['situacao'] == 'Aberta') & 
#                                    (pd.to_datetime(contas_receber['data_vencimento'])
#                                    .dt.month == int(mes))]



#valor_pago = contas_pagas['valor'].sum()
#valor_aberto = contas_abertas['valor'].sum()

#st.write(f'Valor pago: R${valor_pago:.2f}')
#st.write(f'Valor aberto: R${valor_aberto:.2f}')

# RECEBIMENTOS
contas_receber['mes_pagamento'] = contas_receber['mes_pagamento'].dropna().astype(int)
pivot_recebimentos = contas_receber.pivot_table(
    index=[],
    columns='mes_pagamento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)

pivot_recebimentos.index = pd.Index(['Recebido'])
# Opcional: coloca um nome para a linha
#st.write('Recebimentos')
#st.dataframe(pivot_recebimentos)
#st.divider()

#FLUXO REAL
contas_receber['mes_recebimento'] = contas_receber['mes_recebimento'].dropna().astype(int)
pivot_fluxo_real = contas_receber.pivot_table(
    index=[],
    columns='mes_recebimento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)
#st.write('Fluxo real de entradas')
#st.dataframe(pivot_fluxo_real)
#st.divider()



# ALUNOS
pivot_alunos = contas_pagas.groupby('mes_pagamento')['cliente'].nunique().reset_index()

# Transpõe para que cada coluna seja um mês e o valor seja a quantidade de alunos
pivot_alunos = pivot_alunos.set_index('mes_pagamento').T

# Opcional: renomeia a linha
pivot_alunos.index = pd.Index(['Quantidade de alunos'])

st.write('Quantidade de alunos')
st.dataframe(pivot_alunos)

st.divider()
contas_pagar = pd.read_sql(f"Select * from contas_pagar where unidade = '{unidade}'", engine)
contas_pagar['titulo'] = contas_pagar['titulo'].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()


contas_pagar['mes_pagamento'] = contas_pagar['mes_pagamento'].dropna().astype(int)
pivot_contas_pagar = contas_pagar.pivot_table(
    index=[],
    columns='mes_pagamento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)
#st.write('Saídas')
#st.dataframe(pivot_contas_pagar)
#st.divider()
# Garante que os dois DataFrames tenham as mesmas colunas (meses)
todos_meses = sorted(set(pivot_recebimentos.columns).union(set(pivot_contas_pagar.columns)))
pivot_recebimentos = pivot_recebimentos.reindex(columns=todos_meses, fill_value=0)
pivot_contas_pagar = pivot_contas_pagar.reindex(columns=todos_meses, fill_value=0)

# Calcula o lucro/saldo por mês
lucro = pivot_recebimentos.values - pivot_contas_pagar.values

# Cria um novo DataFrame com Recebido, Saídas e Lucro
df_fluxo = pd.DataFrame(
    data = np.vstack([pivot_recebimentos.values, pivot_contas_pagar.values, lucro]),
    index = ['Recebido', 'Saídas', 'Lucro'],
    columns = todos_meses
)
df_fluxo['Total'] = df_fluxo.sum(axis=1)

st.write('Fluxo consolidado (Recebido, Saídas, Lucro)')
st.dataframe(df_fluxo)


# Garante que pivot_fluxo_real e pivot_contas_pagar tenham as mesmas colunas (meses)
todos_meses_real = sorted(set(pivot_fluxo_real.columns).union(set(pivot_contas_pagar.columns)))
pivot_fluxo_real = pivot_fluxo_real.reindex(columns=todos_meses_real, fill_value=0)
pivot_contas_pagar_real = pivot_contas_pagar.reindex(columns=todos_meses_real, fill_value=0)

# Calcula o saldo real por mês
saldo_real = pivot_fluxo_real.values - pivot_contas_pagar_real.values

# Cria um novo DataFrame com Entradas Reais, Saídas e Saldo Real
df_fluxo_real = pd.DataFrame(
    data = np.vstack([pivot_fluxo_real.values, pivot_contas_pagar_real.values, saldo_real]),
    index = ['Entradas Reais', 'Saídas', 'Saldo Real'],
    columns = todos_meses_real
)
df_fluxo_real['Total'] = df_fluxo_real.sum(axis=1)

st.write('Fluxo Real consolidado (Entradas Reais, Saídas, Saldo Real)')
st.dataframe(df_fluxo_real)

# Calcula a diferença percentual mês a mês (exceto a coluna 'Total')
df_percent = df_fluxo.iloc[:, :-1].pct_change(axis=1) * 100
df_percent = df_percent.round(2)



# Ajusta os nomes das linhas para indicar que é percentual
df_percent.index = pd.Index([f"{idx} (%)" for idx in df_fluxo.index])

# Junta ao DataFrame original para exibir juntos (opcional)


st.write('Fluxo consolidado (Recebido, Saídas, Lucro) com variação percentual')
st.dataframe(df_percent)


# Garante que mes_pagamento é inteiro
contas_pagar['mes_pagamento'] = contas_pagar['mes_pagamento'].astype(int)

# Cria a tabela dinâmica: linhas = titulo, colunas = mes_pagamento, valores = soma dos gastos
pivot_titulos = contas_pagar.pivot_table(
    index='titulo',
    columns='mes_pagamento',
    values='valor',
    aggfunc='sum',
    fill_value=0
)

# (Opcional) Adiciona uma coluna de total por título
pivot_titulos['Total'] = pivot_titulos.sum(axis=1)

# (Opcional) Adiciona uma linha de total por mês
pivot_titulos.loc['Total'] = pivot_titulos.sum(axis=0)

#st.write('Gastos por título e mês')
#st.dataframe(pivot_titulos)

# Calcula a diferença absoluta mês a mês para cada título (ignora a coluna 'Total' e a linha 'Total')
pivot_titulos_diff = pivot_titulos.drop('Total', errors='ignore').iloc[:, :-1].diff(axis=1).fillna(0)

# (Opcional) Adiciona uma linha de total das diferenças por mês
pivot_titulos_diff.loc['Total'] = pivot_titulos_diff.sum(axis=0)

st.write('Diferença absoluta de gastos por título e mês (mês atual - mês anterior)')
st.dataframe(pivot_titulos_diff)
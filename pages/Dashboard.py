import streamlit as st
import pandas as pd
from src.db.db import engine
import numpy as np


unidade = st.selectbox("Selecione unidade", ['MOK','Shopping'])
stone = pd.read_sql(f"Select * from stone where unidade = '{unidade}'", engine)
contas_receber = pd.read_sql(f"Select * from contas_receber  where unidade = '{unidade}'", engine)
meses = ['Sem filtro']
meses_unicos = contas_receber['mes_pagamento'].dropna().unique()
meses += sorted([str(int(m)) for m in meses_unicos if pd.notnull(m)])



#mes = st.selectbox('Mês', meses)


contas_pagas = contas_receber[contas_receber['situacao'] == 'Paga']
contas_abertas = contas_receber[contas_receber['situacao'] == 'Aberta']

cartoes_stone = stone[['data_venda','data_vencimento','valor_bruto']]
pagamentos_seufisio = contas_pagas[~contas_pagas['forma'].isin(['Cartão de crédito','Cartão de débito'])]


# RECEBIMENTOS
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
pivot_stone.rename(columns={'valor_liquido':'valor', 'mes_vencimento':'mes_pagamento'})
pivot_stone.index = pd.Index(['Recebido'])


concat_stone_seufisio = pivot_stone + pivot_recebimentos


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

todos_meses = sorted(set(pivot_recebimentos.columns).union(set(pivot_contas_pagar.columns)))
pivot_recebimentos = concat_stone_seufisio.reindex(columns=todos_meses, fill_value=0)
pivot_contas_pagar = pivot_contas_pagar.reindex(columns=todos_meses, fill_value=0)

# Calcula o lucro/saldo por mês
lucro = pivot_recebimentos.values - pivot_contas_pagar.values

# Cria um novo DataFrame com Recebido, Saídas e Lucro
df_fluxo = pd.DataFrame(
    data = np.vstack([concat_stone_seufisio.values, pivot_contas_pagar.values, lucro]),
    index = ['Recebido', 'Saídas', 'Lucro'],
    columns = todos_meses
)
df_fluxo['Total'] = df_fluxo.sum(axis=1)

st.write('Fluxo consolidado (Recebido, Saídas, Lucro)')
st.dataframe(df_fluxo)

###################################




# Calcula a diferença percentual mês a mês (exceto a coluna 'Total')
df_percent = df_fluxo.iloc[:, :-1].pct_change(axis=1) * 100
df_percent = df_percent.round(2)



# Ajusta os nomes das linhas para indicar que é percentual
df_percent.index = pd.Index([f"{idx} (%)" for idx in df_fluxo.index])

# Junta ao DataFrame original para exibir juntos (opcional)





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
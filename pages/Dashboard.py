import streamlit as st
import pandas as pd
import sqlalchemy
from src.controllers import relatorio_controller as rc
import os
from dotenv import load_dotenv

def atualizar_arquivos_temporarios():
    DB_URL = os.getenv("DB_URL")
    engine = sqlalchemy.create_engine(f'{DB_URL}') 
    categorias= ["contas_receber", "contas_pagar", "atendimentos", "stone"]
    for i in categorias:
        if os.path.exists(f"temp_{i}.csv"):
            os.remove(f"temp_{i}.csv")
            pd.read_sql_query(f"Select * from {i}", engine).to_csv(f"temp_{i}.csv")
        else:
            pd.read_sql_query(f"Select * from {i}", engine).to_csv(f"temp_{i}.csv")


load_dotenv()

st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("📊 Dashboard Financeiro - Receitas x Despesas")



if st.button('Atualizar', key= "df"):
    atualizar_arquivos_temporarios()



df_receber = pd.read_csv("temp_contas_receber.csv")
df_pagar = pd.read_csv("temp_contas_pagar.csv")

# Filtro de mês
meses_receber = sorted(df_receber['mes_recebimento'].dropna().unique().tolist())
meses_pagar = sorted(df_pagar['mes_pagamento'].dropna().unique().tolist())
meses = sorted(list(set([int(m) for m in meses_receber + meses_pagar if pd.notnull(m)])))
mes = st.selectbox("Selecione o mês", ['Sem Filtro'] + [str(m) for m in meses], key='mes')

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Recebido", f"{rc.get_recebimentos_totais(df_receber, mes):,.2f}")
with col2:
    st.metric("Total Pago", f"{rc.get_pagamentos_totais(df_pagar, mes):,.2f}")
with col3:
    st.metric("Saldo", f"{rc.get_recebimentos_totais(df_receber, mes) - rc.get_pagamentos_totais(df_pagar, mes):,.2f}")

# Evolução do fluxo de caixa
st.subheader("Evolução do Fluxo de Caixa")
df_fluxo = rc.fluxo_caixa_total(df_receber, df_pagar, mes)
st.write(df_fluxo)

st.subheader("Evolução Mensal do Fluxo de Caixa")
df_evolucao = rc.evolucao_fluxo_caixa(df_receber, df_pagar)
st.dataframe(df_evolucao)

# Gráficos de agrupamento - todos ordenados do maior para o menor
st.subheader("Recebimentos por Centro de Custo")
df_centro_custo = rc.get_despesas_centro_custo(df_receber, mes)
df_centro_custo_sorted = df_centro_custo.sort_values(by='valor', ascending=True)
st.bar_chart(df_centro_custo_sorted.set_index('centro_de_custo'))

st.subheader("Recebimentos por Forma")
df_forma = rc.get_despesas_forma(df_receber, mes)
df_forma_sorted = df_forma.sort_values(by='valor', ascending=False)
st.bar_chart(df_forma_sorted.set_index('forma'))

# st.subheader("Recebimentos por Categoria")
# df_categoria = rc.get_despesas_categoria(df_receber, mes)
# df_categoria_sorted = df_categoria.sort_values(by='valor', ascending=False)
# st.bar_chart(df_categoria_sorted.set_index('categoria'))

st.subheader("Pagamentos por Fornecedor")
df_fornecedor = rc.get_despesas_fornecedor(df_pagar, mes)
df_fornecedor_sorted = df_fornecedor.sort_values(by='valor', ascending=False)
st.bar_chart(df_fornecedor_sorted.set_index('fornecedor'))

# Total de clientes
st.subheader("Total de Clientes")
st.write(rc.get_total_clientes(df_receber, mes))

df_clientes_pivot = rc.clientes_unicos_por_mes(df_receber)
st.dataframe(df_clientes_pivot)
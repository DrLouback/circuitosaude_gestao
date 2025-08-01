import streamlit as st
from src.transformers.ContasReceberTransformer import ContasReceberTransformer
from src.transformers.ContasPagarTransformer import ContasPagarTransformer
from src.transformers.AtendimentosTransformer import AtendimentosTransformer
from src.models.ContasReceber import ContasReceber
from src.models.ContasPagar import ContasPagar
from src.models.Atendimentos import Atendimentos
from src.utils.input_db_generics import input_db
from src.utils.pdf_extract import extract_pdf
import asyncio
import pandas as pd
from src.transformers.StoneTransformer import StoneTransformer
from src.models.Stone import Stone

SELECT_BOX_OPTIONS = [
    'Contas a receber',
    'Contas a pagar',
    'Atendimentos',
    'ChatBot',
    'Stone'
]

st.title('Ingestão de dados')
unidade = st.pills("selecione a unidade", ['MOK', 'Shopping'])
categoria = st.selectbox("Selecione a categoria de dados", SELECT_BOX_OPTIONS, key="text")
dados = st.file_uploader("Escolha um arquivo", type=["pdf", "xlsx", 'xls', 'csv'], key="file")

def processar_contas_receber(df, unidade):
    transformer = ContasReceberTransformer(df, unidade)
    input_db(transformer.dataframe(), ContasReceber, conflict_column='id_conta_receber')

def processar_contas_pagar(df, unidade):
    transformer = ContasPagarTransformer(df, unidade)
    input_db(transformer.dataframe(), ContasPagar, conflict_column='id_conta_pagar')

def processar_atendimentos(df, unidade):
    transformer = AtendimentosTransformer(df, unidade)
    input_db(transformer.dataframe(), Atendimentos, conflict_column='')

def processar_chatbot(df, unidade):
    st.info("Funcionalidade de ChatBot ainda não implementada.")

def processar_stone(df: pd.DataFrame, unidade):
    print(df.columns)
    transformer = StoneTransformer(df, unidade)
    input_db(transformer.dataframe(), Stone, conflict_column='id_stone_unidade')

PROCESSADORES = {
    'Contas a receber': processar_contas_receber,
    'Contas a pagar': processar_contas_pagar,
    'Atendimentos': processar_atendimentos,
    'ChatBot': processar_chatbot,
    'Stone': processar_stone,
}

async def executar_processamento(categoria, df_extracted, unidade):
    await asyncio.to_thread(PROCESSADORES[categoria], df_extracted, unidade)

if st.button("Enviar"):
    if categoria in SELECT_BOX_OPTIONS and dados is not None:
        try:
            if categoria != "Stone":
                df_extracted = extract_pdf(dados)
            else:
                try:
                    df_extracted = pd.read_excel(dados)
                except:
                    df_extracted = pd.read_csv(dados, sep= ';')

            with st.spinner("Processando..."):
                asyncio.run(executar_processamento(categoria, df_extracted, unidade))
                
            st.success(f"{categoria} processada com sucesso!")
            
        except Exception as e:
            st.error(f"Erro ao processar {categoria}: {e}")
    else:
        st.warning("Selecione uma categoria e faça o upload de um arquivo.")
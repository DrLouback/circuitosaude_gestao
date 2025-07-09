import streamlit as st
from src.transformers.ContasReceberTransformer import ContasReceberTransformer
from src.transformers.ContasPagarTransformer import ContasPagarTransformer
from src.transformers.AtendimentosTransformer import AtendimentosTransformer
from src.models.ContasReceber import ContasReceber
from src.models.ContasPagar import ContasPagar
from src.models.Atendimentos import Atendimentos
from src.utils.input_db_generics import input_db
from src.utils.pdf_extract import extract_pdf

st.header("Hello")

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
    input_db(transformer.dataframe(), ContasReceber)

def processar_contas_pagar(df, unidade):
    transformer = ContasPagarTransformer(df, unidade)
    input_db(transformer.dataframe(), ContasPagar)

def processar_atendimentos(df, unidade):
    transformer = AtendimentosTransformer(df, unidade)
    input_db(transformer.dataframe(), Atendimentos)

def processar_chatbot(df, unidade):
    st.info("Funcionalidade de ChatBot ainda não implementada.")

def processar_stone(df, unidade):
    st.info("Funcionalidade de Stone ainda não implementada.")

PROCESSADORES = {
    'Contas a receber': processar_contas_receber,
    'Contas a pagar': processar_contas_pagar,
    'Atendimentos': processar_atendimentos,
    'ChatBot': processar_chatbot,
    'Stone': processar_stone,
}

if st.button("Enviar"):
    if categoria in SELECT_BOX_OPTIONS and dados is not None:
        try:
            df_extracted = extract_pdf(dados)
            PROCESSADORES[categoria](df_extracted, unidade)
            st.success(f"{categoria} processada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao processar {categoria}: {e}")
    else:
        st.warning("Selecione uma categoria e faça o upload de um arquivo.")
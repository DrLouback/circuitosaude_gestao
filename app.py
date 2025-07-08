import streamlit as st
from src.transformers.ContasReceberTransformer import ContasReceberTransformer
from src.models.ContasReceber import ContasReceber
from src.utils.input_db_generics import input_db
from src.utils.pdf_extract import extract_pdf

st.header("Hello")

SELECT_BOX_OPTIONS = ['Contas a receber', 'Contas a pagar', 'Atendimentos', 'ChatBot', 'Stone']

st.title('Ingestão de dados')
unidade = st.pills("selecione a unidade", ['MOK','Shopping'])

categoria = st.selectbox("Selecione a categoria de dados", SELECT_BOX_OPTIONS , key="text")

dados = st.file_uploader("Escolha um arquivo", type=["pdf", "xlsx",'xls','csv'], key="file")


if st.button("Enviar"):
    if categoria in SELECT_BOX_OPTIONS:
        if categoria == 'Contas a receber':
            try:
                df_extracted = extract_pdf(dados)
                transformado = ContasReceberTransformer(df_extracted, unidade)
                input_db(transformado.dataframe(), ContasReceber)
            except Exception as e:
                raise Exception(f'{e}')
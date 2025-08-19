import streamlit as st
import pandas as pd
from src.transformers.ContasReceberTransformer import ContasReceberTransformer
from src.transformers.ContasPagarTransformer import ContasPagarTransformer
from src.transformers.AtendimentosTransformer import AtendimentosTransformer
from src.transformers.StoneTransformer import StoneTransformer
from src.models.ContasReceber import ContasReceber
from src.models.ContasPagar import ContasPagar
from src.models.Atendimentos import Atendimentos
from src.models.Stone import Stone
from src.utils.input_db_generics import input_db
from src.utils.pdf_extract import extract_pdf

from src.db.db import conn

SELECT_BOX_OPTIONS = [
    'Contas a receber',
    'Contas a pagar',
    'Atendimentos',
    'ChatBot',
    'Stone'
]

st.title('Ingestão de dados')
unidade = st.pills("Selecione a unidade", ['MOK', 'Shopping'])
categoria = st.selectbox("Selecione a categoria de dados", SELECT_BOX_OPTIONS, key="text")
dados = st.file_uploader("Escolha um arquivo", type=["pdf", "xlsx", "xls", "csv"], key="file")


def processar_contas_receber(df, unidade):
    try:
        try:
            transformer = ContasReceberTransformer(df, unidade)
        except Exception as e:
            st.error("Erro no transformer")
        input_db(transformer.dataframe(), ContasReceber, conflict_column='id_conta_receber')
    except Exception as e:
        st.error(f"Erro ao processar Contas a Receber: {e}")


def processar_contas_pagar(df, unidade):
    try:
        transformer = ContasPagarTransformer(df, unidade)
        input_db(transformer.dataframe(), ContasPagar, conflict_column='id_conta_pagar')
    except Exception as e:
        st.error(f"Erro ao processar Contas a Pagar: {e}")


def processar_atendimentos(df: pd.DataFrame, unidade):
    try:
        #transformer = AtendimentosTransformer(df, unidade)
        df['unidade'] = unidade
    
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        df['data'] = df['Data/Hora'].dt.date

        df['hora'] = df['Data/Hora'].dt.time
        df['mes'] = df['Data/Hora'].dt.month
        transformer = AtendimentosTransformer(df, unidade)
        input_db(transformer.dataframe(), Atendimentos)
    except Exception as e:
        st.error(f"Erro ao processar Atendimentos: {e}")


def processar_chatbot(df, unidade):
    st.info("Funcionalidade de ChatBot ainda não implementada.")


def processar_stone(df, unidade):
    try:
        transformer = StoneTransformer(df, unidade)
        input_db(transformer.dataframe(), Stone, conflict_column='id_stone_unidade')
    except Exception as e:
        st.error(f"Erro ao processar Stone: {e}")


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
            # Extrair dataframe
            if categoria != "Stone":
                df_extracted = extract_pdf(dados)
            else:
                try:
                    df_extracted = pd.read_excel(dados)
                except Exception:
                    df_extracted = pd.read_csv(dados, sep=';')

            with st.spinner("Processando..."):
                # Chama o processador correspondente
                PROCESSADORES[categoria](df_extracted, unidade)

            st.success(f"{categoria} processada com sucesso!")

        except Exception as e:
            st.error(f"Erro geral ao processar {categoria}: {e}")
    else:
        st.warning("Selecione uma categoria e faça o upload de um arquivo.")

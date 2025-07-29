from src.controllers.AtendimentosController import atendimentos_json
import streamlit as st

st.dataframe(atendimentos_json())
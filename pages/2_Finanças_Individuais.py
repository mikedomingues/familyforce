import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestão Pessoal", page_icon="👤")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Por favor, faça login na página principal.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

st.title(f"👤 Gestão Pessoal: {st.session_state.username}")

# Filtramos a aba apenas para o utilizador logado
df_ind = conn.read(worksheet="financas_individuais", ttl=0)
meus_dados = df_ind[df_ind["utilizador"] == st.session_state.username]

if meus_dados.empty:
    st.info("Ainda não tens registos pessoais.")
else:
    st.dataframe(meus_dados, use_container_width=True)

with st.form("add_pessoal"):
    st.subheader("Novo Registo Pessoal")
    v = st.number_input("Valor", step=0.01)
    d = st.text_input("Descrição")
    if st.form_submit_button("Adicionar"):
        # Lógica para guardar na aba financas_individuais
        st.write("Funcionalidade de escrita em desenvolvimento...")

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestão Pessoal", page_icon="👤")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Por favor, faça login na página principal.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title(f"👤 Gestão Pessoal: {st.session_state.username}")

try:
    df_ind = conn.read(worksheet="financas_individuais", ttl=0)
    df_ind.columns = df_ind.columns.str.strip()

    # Alterado para 'User_ID' conforme detectado na tua imagem
    if "User_ID" in df_ind.columns:
        # Nota: Se o User_ID no Sheets for o número (1, 2, 3), 
        # precisamos comparar com o ID. Se for o nome, usamos o username.
        # Vamos tentar filtrar pelo nome primeiro:
        meus_dados = df_ind[df_ind["User_ID"] == st.session_state.username]
        
        if meus_dados.empty:
            st.info(f"Ainda não existem registos para {st.session_state.username}.")
        else:
            st.dataframe(meus_dados, use_container_width=True)
    else:
        st.error("❌ Coluna 'User_ID' não encontrada na aba 'financas_individuais'.")
        st.info(f"Colunas detetadas: {', '.join(df_ind.columns)}")

except Exception as e:
    st.error(f"Erro ao ler a aba: {e}")

st.divider()

with st.form("add_pessoal"):
    st.subheader("➕ Novo Registo")
    d = st.text_input("Descrição")
    v = st.number_input("Valor", step=0.01)
    if st.form_submit_button("Guardar"):
        st.info("Funcionalidade de gravação em teste. Verifique os nomes das colunas.")

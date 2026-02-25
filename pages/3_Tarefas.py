import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Tarefas", page_icon="✅")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Por favor, faça login na página principal.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title("✅ Tarefas da Família")

df_tarefas = conn.read(worksheet="tarefas", ttl=0)
st.table(df_tarefas)

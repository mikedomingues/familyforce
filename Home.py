import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# Ligação
conn = st.connection("gsheets", type=GSheetsConnection)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    with st.form("login"):
        user_input = st.text_input("Utilizador")
        pass_input = st.text_input("Palavra-passe", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            try:
                # TTL=0 força o Streamlit a ler dados novos e ignorar erros antigos
                df_u = conn.read(worksheet="users", ttl=0)
                
                # Limpa espaços nas colunas e dados para evitar erros de digitação
                df_u.columns = df_u.columns.str.strip()
                df_u['nome'] = df_u['nome'].astype(str).str.strip()
                df_u['password'] = df_u['password'].astype(str).str.strip()
                
                # Validação
                auth = df_u[(df_u["nome"] == user_input) & (df_u["password"] == pass_input)]
                
                if not auth.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.session_state.perfil = auth.iloc[0]["perfil"]
                    st.rerun()
                else:
                    st.error("Utilizador ou password incorretos.")
            except Exception as e:
                st.error(f"Erro de Ligação: Verifique se o Sheets está partilhado com o email da Service Account.")
                st.info(f"Detalhe técnico: {e}")
    st.stop()

# --- DASHBOARD APÓS LOGIN ---
st.title(f"🏠 Bem-vindo, {st.session_state.username}!")

st.write("### ⚡ Atalhos Rápidos")
c1, c2, c3 = st.columns(3)
if c1.button("💰 Finanças Gerais", use_container_width=True):
    st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal", use_container_width=True):
    st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("🚪 Sair", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

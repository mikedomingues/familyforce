import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração Base
st.set_page_config(page_title="Domingues Family Hub", layout="wide")

# Ligação
conn = st.connection("gsheets", type=GSheetsConnection)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Acesso Família Domingues")
    
    with st.form("login_form"):
        u_name = st.text_input("Utilizador")
        u_pass = st.text_input("Password", type="password")
        
        if st.form_submit_button("Entrar"):
            try:
                # Tenta ler a aba 'users'
                df_u = conn.read(worksheet="users", ttl=0)
                # Verifica credenciais
                user_match = df_u[(df_u['nome'] == u_name) & (df_u['password'] == u_pass)]
                
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user = u_name
                    st.session_state.perfil = user_match.iloc[0]['perfil']
                    st.rerun()
                else:
                    st.error("Utilizador ou password incorretos.")
            except Exception as e:
                st.error("Erro ao aceder ao Sheets. Verifique os Secrets.")
                st.info(f"Detalhe: {e}")
    st.stop()

# --- DASHBOARD ---
st.title(f"🏠 Olá, {st.session_state.user}!")
st.sidebar.write(f"Perfil: {st.session_state.perfil}")

# Botões de Navegação
st.subheader("🚀 Navegação")
c1, c2, c3 = st.columns(3)

if c1.button("💰 Finanças Gerais"):
    st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal"):
    st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("🚪 Sair"):
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# Gráfico Simples
try:
    df_g = conn.read(worksheet="financas_gerais", ttl=0)
    if not df_g.empty:
        st.subheader("📊 Resumo de Gastos")
        st.bar_chart(df_g.groupby("Categoria")["Valor"].sum())
except:
    st.info("Aguardando dados para exibir gráficos.")

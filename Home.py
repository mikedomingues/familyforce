import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# Ligação ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. SISTEMA DE LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = ""
    st.session_state.perfil = ""

if not st.session_state.authenticated:
    st.title("🔐 Login - Domingues Family")
    
    # Carrega utilizadores diretamente do Sheets
    try:
        users_df = conn.read(worksheet="users", ttl=0)
        user_list = users_df['nome'].tolist()
    except:
        user_list = []

    with st.form("login_form"):
        user = st.selectbox("Seleccione o Utilizador", user_list)
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_button("Entrar", use_container_width=True)
        
        if submit:
            auth = users_df[(users_df['nome'] == user) & (users_df['password'] == pw)]
            if not auth.empty:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.perfil = auth.iloc[0]['perfil']
                st.rerun()
            else:
                st.error("Dados incorretos.")
    st.stop()

# --- 2. DASHBOARD (HOME) APÓS LOGIN ---
st.sidebar.title(f"👋 Olá, {st.session_state.user}!")
st.sidebar.info(f"Nível de Acesso: {st.session_state.perfil}")

st.title("🏠 Painel Principal")
st.write(f"Bem-vindo ao centro de gestão da família, **{st.session_state.user}**.")

# --- 3. METRICAS RÁPIDAS (RESUMO) ---
st.subheader("📊 Resumo do Mês")
m1, m2, m3 = st.columns(3)

try:
    df_geral = conn.read(worksheet="financas_gerais", ttl=0)
    df_tarefas = conn.read(worksheet="tarefas", ttl=0)
    
    total_gasto = df_geral["Valor"].sum() if not df_geral.empty else 0
    tarefas_pendentes = len(df_tarefas[df_tarefas["status"] == "Pendente"]) if not df_tarefas.empty else 0
    
    m1.metric("Gastos Gerais", f"{total_gasto:.2f} €")
    m2.metric("Tarefas Pendentes", tarefas_pendentes)
    m3.metric("Utilizadores Ativos", "3")
except:
    st.warning("A carregar dados do Sheets...")

st.divider()

# --- 4. ATALHOS PARA PÁGINAS ---
st.subheader("🚀 Atalhos Rápidos")
col1, col2, col3 = st.columns(3)

if col1.button("💰 Ir para Finanças", use_container_width=True):
    st.switch_page("pages/1_Finanças_Gerais.py")

if col2.button("✅ Ir para Tarefas", use_container_width=True):
    st.switch_page("pages/3_Tarefas.py")

if col3.button("👤 Gestão Pessoal", use_container_width=True):
    st.switch_page("pages/2_Finanças_Individuais.py")

st.write("---")

# --- 5. ALERTAS ---
if st.session_state.perfil in ["Master", "Admin"]:
    st.success("🛠️ Modo Administrador Ativo: Podes editar todas as secções.")
else:
    st.info("ℹ️ Modo Visualizador: Podes ver os dados e gerir apenas as tuas tarefas.")

# Botão Sair na Sidebar
if st.sidebar.button("Terminar Sessão"):
    st.session_state.authenticated = False
    st.rerun()

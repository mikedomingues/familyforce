import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# 2. Ligação ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Estado de Sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- ECRÃ DE LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    # Criamos um expander de ajuda caso os utilizadores não apareçam
    with st.sidebar:
        if st.button("Verificar Ligação (Debug)"):
            try:
                test_df = conn.read(worksheet="users", ttl=0)
                st.success("✅ Aba 'users' encontrada!")
                st.write(test_df.head())
            except Exception as e:
                st.error(f"❌ Erro: {e}")

    with st.form("login"):
        user = st.text_input("Utilizador (Miguel, Raquel ou Gabriel)")
        pw = st.text_input("Palavra-passe", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            try:
                # Validação contra a aba 'users'
                df_u = conn.read(worksheet="users", ttl=0)
                auth = df_u[(df_u["nome"] == user) & (df_u["password"] == pw)]
                
                if not auth.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.perfil = auth.iloc[0]["perfil"]
                    st.rerun()
                else:
                    st.error("Utilizador ou password incorretos.")
            except:
                st.error("Erro ao ler aba 'users'. Verifique os Secrets.")
    st.stop()

# --- DASHBOARD (APÓS LOGIN) ---
st.title(f"👋 Olá, {st.session_state.username}!")
st.sidebar.info(f"Perfil: {st.session_state.perfil}")

# Atalhos rápidos (Estilo app(1).py)
st.subheader("🚀 Atalhos Rápidos")
c1, c2, c3 = st.columns(3)

if c1.button("💰 Finanças Gerais", use_container_width=True):
    st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal", use_container_width=True):
    st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("✅ Tarefas", use_container_width=True):
    st.switch_page("pages/3_Tarefas.py")

st.divider()

# Métricas no Dashboard
try:
    df_g = conn.read(worksheet="financas_gerais", ttl=0)
    if not df_g.empty:
        total = df_g["Valor"].sum()
        st.subheader("📊 Resumo Financeiro")
        m1, m2 = st.columns(2)
        m1.metric("Gasto Total Acumulado", f"{total:.2f} €")
        
        # Gráfico simples
        st.bar_chart(df_g.groupby("Categoria")["Valor"].sum())
except:
    st.info("A aguardar dados financeiros para gerar gráficos.")

if st.sidebar.button("Terminar Sessão"):
    st.session_state.logged_in = False
    st.rerun()

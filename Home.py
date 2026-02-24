import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página baseada no seu modelo
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# --- 1. LIGAÇÃO E CARREGAMENTO INICIAL ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_initial_data():
    try:
        # Tenta ler a aba 'users' conforme a sua imagem
        df_u = conn.read(worksheet="users", ttl=0)
        # Tenta ler as abas financeiras e tarefas para o dashboard
        df_g = conn.read(worksheet="financas_gerais", ttl=0)
        df_t = conn.read(worksheet="tarefas", ttl=0)
        return df_u, df_g, df_t
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_u, df_g, df_t = load_initial_data()

# --- 2. SISTEMA DE LOGIN (Estrutura do app (1).py) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    # Verifica se os utilizadores foram carregados
    if df_u.empty:
        st.error("⚠️ Erro: Não foi possível carregar a lista de utilizadores. Verifique os Secrets e a aba 'users'.")
        st.stop()

    with st.form("login"):
        # Selectbox preenchido com a coluna 'nome' da sua imagem
        user_select = st.selectbox("Seleccione o Utilizador", df_u["nome"].tolist())
        pass_input = st.text_input("Palavra-passe", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            # Validação contra a folha
            auth = df_u[(df_u["nome"] == user_select) & (df_u["password"] == pass_input)]
            
            if not auth.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_select
                st.session_state.perfil = auth.iloc[0]["perfil"]
                st.rerun()
            else:
                st.error("Utilizador ou Palavra-passe incorretos")
    st.stop()

# --- 3. LAYOUT DO DASHBOARD (Estilo app (1).py) ---
st.title(f"👋 Olá, {st.session_state.username}!")
st.sidebar.info(f"Perfil: {st.session_state.perfil}")

st.write("### ⚡ Atalhos Rápidos")
c1, c2, c3 = st.columns(3)
if c1.button("💰 Finanças Gerais", use_container_width=True):
    st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal", use_container_width=True):
    st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("🚪 Sair", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# --- 4. MÉTRICAS E ALERTAS ---
st.subheader("🔔 Resumo da Família")
m1, m2, m3 = st.columns(3)

if not df_g.empty:
    # Usa coluna 'Valor' da imagem
    total = df_g["Valor"].sum()
    m1.metric("Total Gasto (Comum)", f"{total:.2f} €")
    m2.metric("Última Categoria", df_g["Categoria"].iloc[-1])
else:
    m1.metric("Total Gasto", "0.00 €")

if not df_t.empty:
    # Filtra tarefas pendentes conforme imagem
    pendentes = len(df_t[df_t["Status"] == "Pendente"])
    m3.metric("Tarefas Pendentes", pendentes, delta_color="inverse")

st.divider()

# --- 5. GRÁFICO DE GASTOS ---
if not df_g.empty:
    st.markdown("#### 🔄 Gastos por Categoria")
    # Agrupamento por Categoria da imagem
    chart_data = df_g.groupby("Categoria")["Valor"].sum()
    st.bar_chart(chart_data)

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# --- 1. LIGAÇÃO E CARREGAMENTO DE UTILIZADORES ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar utilizadores (necessária para o Login)
def get_users():
    try:
        # Tenta ler a aba 'users' conforme a tua imagem
        df = conn.read(worksheet="users", ttl=0)
        return df
    except:
        return pd.DataFrame()

df_u = get_users()

# --- 2. SISTEMA DE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    # Verificação se os dados foram lidos
    if df_u.empty:
        st.error("⚠️ Erro: Não foi possível carregar a lista de utilizadores. Verifique se a aba 'users' existe e se o Sheets está partilhado.")
        st.stop()

    with st.form("login"):
        # Aqui carregamos a lista da coluna 'nome'
        user_select = st.selectbox("Selecione o Utilizador", df_u["nome"].unique())
        pass_input = st.text_input("Password", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            # Validação contra a folha users
            auth = df_u[(df_u["nome"] == user_select) & (df_u["password"] == pass_input)]
            
            if not auth.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_select
                st.session_state.perfil = auth.iloc[0]["perfil"]
                st.rerun()
            else:
                st.error("Password incorreta")
    st.stop()

# --- 3. DASHBOARD APÓS LOGIN (Estilo app (1).py) ---
st.title(f"👋 Olá, {st.session_state.username}!")
st.sidebar.write(f"Utilizador: **{st.session_state.username}**")
st.sidebar.write(f"Acesso: **{st.session_state.perfil}**")

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

# --- 4. CARREGAMENTO DE DADOS FINANCEIROS ---
def load_data():
    try:
        # Lê as abas conforme as tuas imagens
        df_g = conn.read(worksheet="financas_gerais", ttl=0)
        df_t = conn.read(worksheet="tarefas", ttl=0)
        return df_g, df_t
    except:
        return pd.DataFrame(), pd.DataFrame()

df_g, df_t = load_data()

# --- 5. MÉTRICAS DO DASHBOARD ---
st.subheader("📊 Resumo da Família")
m1, m2, m3 = st.columns(3)

if not df_g.empty:
    # Usa a coluna 'Valor' da imagem
    total = df_g["Valor"].sum()
    m1.metric("Total Gasto (Comum)", f"{total:,.2f} €")
    
    # Última descrição da imagem
    ultima = df_g["Descrição"].iloc[-1] if not df_g.empty else "N/A"
    m2.metric("Última Despesa", ultima)
else:
    m1.metric("Total Gasto", "0.00 €")

if not df_t.empty:
    # Filtra tarefas pendentes da imagem
    pendentes = len(df_t[df_t["Status"] == "Pendente"])
    m3.metric("Tarefas Pendentes", pendentes, delta_color="inverse")

st.divider()

# Gráfico de Gastos (Estilo app (1).py)
if not df_g.empty:
    st.markdown("#### 🔄 Gastos por Categoria")
    chart_data = df_g.groupby("Categoria")["Valor"].sum()
    st.bar_chart(chart_data)

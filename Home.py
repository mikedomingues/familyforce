import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# Inicializar Ligação
conn = st.connection("gsheets", type=GSheetsConnection)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 1. LÓGICA DE LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    try:
        # Carrega a aba 'users' que criaste (image_7d6dbf.png)
        df_u = conn.read(worksheet="users", ttl=0)
        
        with st.form("login_form"):
            # Selectbox com os nomes da coluna 'nome' (image_7d717f.png)
            u_select = st.selectbox("Seleccione o Utilizador", df_u["nome"].tolist())
            p_input = st.text_input("Palavra-passe", type='password')
            
            if st.form_submit_button("Entrar", use_container_width=True):
                # Validação contra a folha
                auth = df_u[(df_u["nome"] == u_select) & (df_u["password"] == p_input)]
                
                if not auth.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = u_select
                    st.session_state.perfil = auth.iloc[0]["perfil"]
                    st.rerun()
                else:
                    st.error("Palavra-passe incorreta.")
    except Exception as e:
        st.error("Erro ao carregar utilizadores. Verifique se partilhou o Sheet com o email da Service Account.")

    st.stop()

# --- 2. DASHBOARD APÓS LOGIN ---
st.title(f"🏠 Bem-vindo, {st.session_state.username}!")
st.sidebar.info(f"Perfil: {st.session_state.perfil}")

# Atalhos Rápidos baseados no teu modelo app (1).py
st.subheader("🚀 Atalhos Rápidos")
c1, c2, c3 = st.columns(3)
if c1.button("💰 Finanças Gerais", use_container_width=True):
    st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal", use_container_width=True):
    st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("🚪 Sair", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# Resumo Financeiro Automático
try:
    df_g = conn.read(worksheet="financas_gerais", ttl=0)
    if not df_g.empty:
        total = df_g["Valor"].sum()
        st.metric("Total Gasto (Geral)", f"{total:.2f} €")
        st.bar_chart(df_g.groupby("Categoria")["Valor"].sum())
except:
    st.info("ℹ️ Adicione dados no Sheets para ver as métricas aqui.")

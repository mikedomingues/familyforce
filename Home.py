import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# 2. Inicializar Ligação
conn = st.connection("gsheets", type=GSheetsConnection)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- ECRÃ DE LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    # Criamos colunas para o formulário ficar centrado e limpo
    col_a, col_b, col_c = st.columns([1,2,1])
    
    with col_b:
        with st.form("login_form"):
            u_input = st.text_input("Utilizador")
            p_input = st.text_input("Palavra-passe", type='password')
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                try:
                    # Tenta ler a aba 'users' - força leitura direta (ttl=0)
                    df_u = conn.read(worksheet="users", ttl=0)
                    
                    # Limpa possíveis espaços nos nomes das colunas e dados
                    df_u.columns = df_u.columns.str.strip()
                    df_u['nome'] = df_u['nome'].astype(str).str.strip()
                    df_u['password'] = df_u['password'].astype(str).str.strip()
                    
                    # Validação
                    auth = df_u[(df_u["nome"] == u_input) & (df_u["password"] == p_input)]
                    
                    if not auth.empty:
                        st.session_state.logged_in = True
                        st.session_state.username = u_input
                        st.session_state.perfil = auth.iloc[0]["perfil"]
                        st.rerun()
                    else:
                        st.error("Utilizador ou password incorretos.")
                except Exception as e:
                    st.error("❌ Erro de Ligação ao Google Sheets")
                    st.warning("Verifica se o email 'familyforce@...' é EDITOR no Sheets.")
                    # Mostra o erro técnico real para sabermos o que se passa
                    st.code(str(e))
    st.stop()

# --- DASHBOARD APÓS LOGIN (Estilo app(1).py) ---
st.title(f"🏠 Olá, {st.session_state.username}!")
st.sidebar.info(f"Perfil: {st.session_state.perfil}")

# Atalhos Rápidos
st.subheader("🚀 Navegação")
c1, c2, c3 = st.columns(3)
if c1.button("💰 Finanças Gerais", use_container_width=True): st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal", use_container_width=True): st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("🚪 Sair", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# Resumo Simples para validar que os dados carregam
try:
    df_g = conn.read(worksheet="financas_gerais", ttl=0)
    if not df_g.empty:
        total = df_g["Valor"].sum()
        st.metric("Total Gasto (Comum)", f"{total:.2f} €")
        st.bar_chart(df_g.groupby("Categoria")["Valor"].sum())
except:
    st.info("ℹ️ Dados financeiros aparecerão aqui após o primeiro registo.")

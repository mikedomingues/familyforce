import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# Inicializar Ligação
conn = st.connection("gsheets", type=GSheetsConnection)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- ECRÃ DE LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    with st.form("login_form"):
        user_input = st.text_input("Utilizador")
        pass_input = st.text_input("Palavra-passe", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            try:
                # ttl=0 força a leitura direta do Google Sheets sem cache
                df_u = conn.read(worksheet="users", ttl=0)
                
                # Validação (Miguel, Raquel ou Gabriel)
                auth = df_u[(df_u["nome"] == user_input) & (df_u["password"] == pass_input)]
                
                if not auth.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.session_state.perfil = auth.iloc[0]["perfil"]
                    st.rerun()
                else:
                    st.error("Utilizador ou password incorretos.")
            except Exception as e:
                st.error("Erro de Ligação: A aba 'users' não foi encontrada ou os Secrets estão incorretos.")
                st.info(f"Detalhe: {e}")
    st.stop()

# --- DASHBOARD APÓS LOGIN ---
else:
    st.title(f"🏠 Bem-vindo, {st.session_state.username}!")
    st.sidebar.info(f"Perfil: {st.session_state.perfil}")

    # Atalhos Rápidos (Baseado no seu ficheiro app(1).py)
    st.subheader("🚀 Atalhos Rápidos")
    c1, c2, c3 = st.columns(3)
    if c1.button("💰 Finanças Gerais", use_container_width=True):
        st.switch_page("pages/1_Finanças_Gerais.py")
    if c2.button("👤 Finanças Individuais", use_container_width=True):
        st.switch_page("pages/2_Finanças_Individuais.py")
    if c3.button("✅ Tarefas", use_container_width=True):
        st.switch_page("pages/3_Tarefas.py")

    st.divider()

    # Resumo Financeiro
    try:
        df_g = conn.read(worksheet="financas_gerais", ttl=0)
        if not df_g.empty:
            total = df_g["Valor"].sum()
            st.metric("Total Gasto (Geral)", f"{total:.2f} €")
            st.bar_chart(df_g.groupby("Categoria")["Valor"].sum())
    except:
        st.info("ℹ️ Adicione dados nas abas financeiras para ver o resumo aqui.")

    if st.sidebar.button("Terminar Sessão"):
        st.session_state.logged_in = False
        st.rerun()

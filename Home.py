import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# 2. Ligação ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Inicializar Estado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- FUNÇÃO PARA TESTAR A LIGAÇÃO ---
def carregar_utilizadores():
    try:
        # Tenta ler a aba 'users'. ttl=0 serve para não guardar cache e ler dados frescos
        df = conn.read(worksheet="users", ttl=0)
        return df
    except Exception as e:
        # Se der erro, mostra o erro técnico para ajudar no suporte
        st.sidebar.error(f"Erro técnico: {e}")
        return pd.DataFrame()

df_u = carregar_utilizadores()

# --- LÓGICA DE LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    if df_u.empty:
        st.error("🚨 Não foi possível carregar os utilizadores.")
        st.info("💡 **Verificações rápidas:**")
        st.markdown("""
        1. O email da Service Account foi adicionado como **Editor** no Google Sheets?
        2. A aba no Sheets chama-se exatamente `users` (em minúsculas)?
        3. Colaste o URL correto do novo Sheets nos **Secrets** desta App?
        """)
        st.stop()

    with st.form("login_form"):
        # Se chegou aqui, os utilizadores foram lidos com sucesso!
        lista_nomes = df_u["nome"].tolist()
        user_select = st.selectbox("Quem é você?", lista_nomes)
        pass_input = st.text_input("Password", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            # Validação
            auth = df_u[(df_u["nome"] == user_select) & (df_u["password"] == pass_input)]
            
            if not auth.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_select
                st.session_state.perfil = auth.iloc[0]["perfil"]
                st.rerun()
            else:
                st.error("Password incorreta.")
    st.stop()

# --- DASHBOARD APÓS LOGIN ---
else:
    st.title(f"👋 Olá, {st.session_state.username}!")
    st.sidebar.button("🚪 Sair", on_click=lambda: st.session_state.update({"logged_in": False}))

    # Atalhos rápidos para as tuas páginas
    st.subheader("🚀 Navegação")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("💰 Finanças Gerais", use_container_width=True):
        st.switch_page("pages/1_Finanças_Gerais.py")
    if col2.button("👤 Gestão Pessoal", use_container_width=True):
        st.switch_page("pages/2_Finanças_Individuais.py")
    if col3.button("✅ Tarefas", use_container_width=True):
        st.switch_page("pages/3_Tarefas.py")

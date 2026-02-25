import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# Ligação ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SISTEMA DE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Acesso Família Domingues")
    
    with st.form("login_form"):
        # Tenta carregar os nomes para o selectbox
        try:
            df_u = conn.read(worksheet="users", ttl=0)
            user_list = df_u["nome"].tolist()
            user_input = st.selectbox("Quem és?", user_list)
        except:
            user_input = st.text_input("Utilizador")

        pass_input = st.text_input("Palavra-passe", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            try:
                df_u = conn.read(worksheet="users", ttl=0)
                auth = df_u[(df_u["nome"] == user_input) & (df_u["password"] == pass_input)]
                
                if not auth.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.session_state.perfil = auth.iloc[0]["perfil"]
                    st.rerun()
                else:
                    st.error("Credenciais incorretas.")
            except Exception as e:
                st.error("Erro de ligação. Verifique se partilhou o Sheet com o email 'familyforce'.")
    st.stop()

# --- DASHBOARD (APÓS LOGIN) ---
st.title(f"🏠 Olá, {st.session_state.username}!")
st.sidebar.write(f"Perfil: **{st.session_state.perfil}**")

# Atalhos Rápidos
st.write("### 🚀 Atalhos")
c1, c2, c3 = st.columns(3)
if c1.button("💰 Finanças Gerais", use_container_width=True): st.switch_page("pages/1_Finanças_Gerais.py")
if c2.button("👤 Gestão Pessoal", use_container_width=True): st.switch_page("pages/2_Finanças_Individuais.py")
if c3.button("🚪 Sair", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# --- PROCESSAMENTO DE DADOS (Estilo app (1).py) ---
try:
    df_g = conn.read(worksheet="financas_gerais", ttl=0)
    df_t = conn.read(worksheet="tarefas", ttl=0)

    st.subheader("📊 Resumo da Casa")
    m1, m2, m3 = st.columns(3)
    
    if not df_g.empty:
        total_gasto = df_g["Valor"].sum()
        m1.metric("Total Gasto (Comum)", f"{total_gasto:.2f} €")
        m2.metric("Última Despesa", df_g["Descrição"].iloc[-1])
    
    if not df_t.empty:
        pendentes = len(df_t[df_t["Status"] == "Pendente"])
        m3.metric("Tarefas Pendentes", pendentes, delta_color="inverse")

    st.write("---")
    
    # Alerta de Tarefas (Baseado na lógica de risco do app(1).py)
    if not df_t.empty and pendentes > 2:
        st.warning(f"⚠️ Atenção! Existem {pendentes} tarefas pendentes. Vamos trabalhar nisso?")
    else:
        st.success("✅ Parabéns! As tarefas estão em dia.")

    # Gráfico de Gastos
    if not df_g.empty:
        st.markdown("#### 🔄 Distribuição por Categoria")
        st.bar_chart(df_g.groupby("Categoria")["Valor"].sum())

except Exception as e:
    st.info("A aguardar preenchimento de dados no Google Sheets para gerar métricas.")

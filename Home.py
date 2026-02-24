import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Domingues Family Hub", layout="wide", page_icon="🏠")

# --- 1. LIGAÇÃO AO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_all_data():
    try:
        # Tenta ler as abas conforme as imagens enviadas
        u = conn.read(worksheet="users", ttl=0)
        g = conn.read(worksheet="financas_gerais", ttl=0)
        t = conn.read(worksheet="tarefas", ttl=0)
        # Limpar espaços nos nomes das colunas para evitar erros
        u.columns = u.columns.str.strip()
        g.columns = g.columns.str.strip()
        t.columns = t.columns.str.strip()
        return u, g, t
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_u, df_g, df_t = load_all_data()

# --- 2. SISTEMA DE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login - Família Domingues")
    
    # Se a folha de utilizadores estiver vazia, mostra erro crítico
    if df_u.empty:
        st.error("⚠️ Erro de Ligação: Não foi possível ler a aba 'users'. Verifique os Secrets e se o Sheets está partilhado com o email da Service Account.")
        st.stop()

    with st.form("login"):
        # Puxa os nomes da coluna 'nome' conforme a imagem image_2b34df.png
        user_select = st.selectbox("Seleccione o Utilizador", df_u["nome"].unique())
        pass_input = st.text_input("Password", type='password')
        
        if st.form_submit_button("Entrar", use_container_width=True):
            # Validação real contra o Sheets
            auth = df_u[(df_u["nome"] == user_select) & (df_u["password"] == pass_input)]
            
            if not auth.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_select
                st.session_state.perfil = auth.iloc[0]["perfil"]
                st.rerun()
            else:
                st.error("Utilizador ou Palavra-passe incorretos")
    st.stop()

# --- 3. DASHBOARD APÓS LOGIN ---
st.title(f"👋 Olá, {st.session_state.username}!")
st.sidebar.write(f"Utilizador: **{st.session_state.username}**")
st.sidebar.info(f"Acesso: {st.session_state.perfil}")

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

# --- 4. MÉTRICAS DO QUADRO GERAL ---
st.subheader("📊 Resumo da Família")
m1, m2, m3 = st.columns(3)

if not df_g.empty:
    # Métricas baseadas na aba 'financas_gerais' (image_6050ff.png)
    total_gasto = df_g["Valor"].sum()
    m1.metric("Total Gasto (Comum)", f"{total_gasto:.2f} €")
    
    # Exibe a última descrição registada
    ultima_desc = df_g["Descrição"].iloc[-1] if not df_g.empty else "N/A"
    m2.metric("Última Despesa", ultima_desc)
else:
    m1.metric("Total Gasto", "0.00 €")

if not df_t.empty:
    # Métricas baseadas na aba 'tarefas' (image_605406.png)
    pendentes = len(df_t[df_t["Status"] == "Pendente"])
    m3.metric("Tarefas Pendentes", pendentes, delta_color="inverse")

st.write("---")

# --- 5. GRÁFICO DE GASTOS ---
if not df_g.empty:
    st.markdown("#### 🔄 Gastos por Categoria")
    # Agrupa pela coluna 'Categoria' da sua imagem
    chart_data = df_g.groupby("Categoria")["Valor"].sum()
    st.bar_chart(chart_data)
else:
    st.info("ℹ️ O gráfico aparecerá assim que existirem dados em 'financas_gerais'.")

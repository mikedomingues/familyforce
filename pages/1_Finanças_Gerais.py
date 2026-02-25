import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestão Pessoal", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

# Título dinâmico e amigável
st.title(f"👤 Espaço Pessoal: {st.session_state.username}")

# Criamos 2 separadores para organizar a vista
tab1, tab2 = st.tabs(["➕ Novo Registo", "📊 Consultar e Gerir"])

with tab1:
    st.subheader("O que queres registar hoje?")
    with st.form("form_novo_gasto", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        data = col1.date_input("Data", datetime.now())
        valor = col2.number_input("Valor (€)", min_value=0.0, step=0.01)
        # Sugestões de categorias para ser mais rápido
        cat = col3.selectbox("Tipo", ["Despesa", "Receita", "Poupanca", "Outro"])
        
        desc = st.text_input("Descrição (Ex: Almoço, Compra Online, Mesada)")
        
        if st.form_submit_button("🚀 Gravar Agora", use_container_width=True):
            if desc and valor > 0:
                try:
                    df_atual = conn.read(worksheet="financas_individuais", ttl=0)
                    nova_linha = pd.DataFrame([{
                        "User_ID": st.session_state.username,
                        "Data": data.strftime("%d/%m/%Y"),
                        "Descrição": desc,
                        "Valor": valor
                    }])
                    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
                    conn.update(worksheet="financas_individuais", data=df_final)
                    st.success("✅ Guardado no Google Sheets!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao gravar: {e}")
            else:
                st.warning("Preenche a descrição e o valor!")

with tab2:
    try:
        df_full = conn.read(worksheet="financas_individuais", ttl=0)
        is_admin = st.session_state.perfil in ["Master", "Admin"]
        
        if is_admin:
            st.info("🔓 Modo Master: Podes editar ou apagar qualquer linha abaixo.")
            # Editor livre para Miguel e Raquel
            edited = st.data_editor(df_full, num_rows="dynamic", use_container_width=True)
            if st.button("💾 Aplicar Correções/Remoções"):
                conn.update(worksheet="financas_individuais", data=edited)
                st.success("Base de dados limpa e atualizada!")
                st.rerun()
        else:
            st.info("📋 Teus registos (apenas leitura). Para correções, pede ao Miguel ou Raquel.")
            # Vista filtrada e protegida para o Gabriel
            df_gabriel = df_full[df_full["User_ID"] == st.session_state.username]
            st.dataframe(df_gabriel, use_container_width=True)
            
    except Exception as e:
        st.error("Ainda não existem dados para mostrar.")

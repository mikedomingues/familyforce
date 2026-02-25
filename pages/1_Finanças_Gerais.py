import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Finanças Gerais", page_icon="💰")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Por favor, faça login na página principal.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💰 Finanças Gerais da Família")

# Leitura dos dados
df = conn.read(worksheet="financas_gerais", ttl=0)

# Métricas rápidas
if not df.empty:
    total = df["Valor"].sum()
    st.metric("Gasto Total Acumulado", f"{total:.2f} €")

# Formulário para Adicionar Gasto (Apenas Master e Admin)
if st.session_state.perfil in ["Master", "Admin"]:
    with st.expander("➕ Registar Nova Despesa Comum"):
        with st.form("add_geral"):
            col1, col2 = st.columns(2)
            data = col1.date_input("Data", datetime.now())
            valor = col2.number_input("Valor (€)", min_value=0.0, step=0.01)
            desc = st.text_input("Descrição (Ex: Mercadona, Renda)")
            cat = st.selectbox("Categoria", ["Casa", "Alimentação", "Lazer", "Saúde", "Outros"])
            
            if st.form_submit_button("Guardar Despesa"):
                nova_linha = pd.DataFrame([{
                    "Data": data.strftime("%d/%m/%Y"),
                    "Descrição": desc,
                    "Valor": valor,
                    "Categoria": cat,
                    "Registado_por": st.session_state.username
                }])
                df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
                conn.update(worksheet="financas_gerais", data=df_atualizado)
                st.success("✅ Despesa guardada!")
                st.rerun()

st.divider()
st.dataframe(df, use_container_width=True)

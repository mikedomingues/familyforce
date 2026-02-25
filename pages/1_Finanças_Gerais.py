import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Finanças Gerais", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title("💰 Finanças Gerais")

try:
    df = conn.read(worksheet="financas_gerais", ttl=0)
    admin_access = st.session_state.perfil in ["Master", "Admin"]

    if admin_access:
        st.info("🔓 Modo Master: Miguel/Raquel (Criar, Editar, Apagar)")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    else:
        st.info("📝 Modo Gabriel: Podes adicionar novos gastos, mas não apagar os existentes.")
        # num_rows="dynamic" permite criar, mas as colunas existentes estão bloqueadas para edição
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, 
                                   disabled=df.columns) # Bloqueia edição das linhas que já existem

    if st.button("💾 Guardar Alterações"):
        conn.update(worksheet="financas_gerais", data=edited_df)
        st.success("✅ Atualizado!")
        st.rerun()

except Exception as e:
    st.error(f"Erro: {e}")

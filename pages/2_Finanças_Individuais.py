import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestão Pessoal", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title(f"👤 Gestão de Registos: {st.session_state.username}")

try:
    df_full = conn.read(worksheet="financas_individuais", ttl=0)
    
    pode_editar_tudo = st.session_state.perfil in ["Master", "Admin"]

    if pode_editar_tudo:
        st.info("🔓 Acesso Total: Podes gerir todos os registos individuais.")
        df_view = df_full
    else:
        # Gabriel só vê as linhas onde o User_ID é o nome dele
        df_view = df_full[df_full["User_ID"] == st.session_state.username]

    # Editor para Admin, apenas Tabela para o Gabriel
    if pode_editar_tudo:
        edited_ind = st.data_editor(df_view, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Confirmar Alterações"):
            conn.update(worksheet="financas_individuais", data=edited_ind)
            st.success("Gravado!")
            st.rerun()
    else:
        st.dataframe(df_view, use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")

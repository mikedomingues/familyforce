import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Tarefas", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title("✅ Gestão de Tarefas")

try:
    df_tarefas = conn.read(worksheet="tarefas", ttl=0)
    admin_access = st.session_state.perfil in ["Master", "Admin"]

    if admin_access:
        edited_tasks = st.data_editor(df_tarefas, num_rows="dynamic", use_container_width=True)
    else:
        st.info("📝 Podes sugerir novas tarefas, mas apenas o Miguel/Raquel as podem validar ou apagar.")
        edited_tasks = st.data_editor(df_tarefas, num_rows="dynamic", use_container_width=True,
                                     disabled=df_tarefas.columns)

    if st.button("💾 Atualizar Lista"):
        conn.update(worksheet="tarefas", data=edited_tasks)
        st.success("✅ Sincronizado!")
        st.rerun()

except Exception as e:
    st.error(f"Erro: {e}")

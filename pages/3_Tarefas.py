import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Tarefas", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title("✅ Gestão de Tarefas")

try:
    df_tarefas = conn.read(worksheet="tarefas", ttl=0)
    
    pode_gerir = st.session_state.perfil in ["Master", "Admin"]

    if pode_gerir:
        st.write("Edita o status ou atribui tarefas aqui:")
        edited_tasks = st.data_editor(df_tarefas, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Atualizar Tarefas"):
            conn.update(worksheet="tarefas", data=edited_tasks)
            st.success("Tarefas atualizadas!")
            st.rerun()
    else:
        st.write("Consulta as tuas tarefas pendentes:")
        st.dataframe(df_tarefas, use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")

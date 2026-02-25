import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Finanças Gerais", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title("💰 Finanças Gerais")

try:
    df = conn.read(worksheet="financas_gerais", ttl=0)
    
    # Verifica se o utilizador tem permissão de edição
    pode_editar = st.session_state.perfil in ["Master", "Admin"]

    if pode_editar:
        st.info("🔓 Modo Editor: Miguel e Raquel podem alterar dados.")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 Guardar Alterações"):
            conn.update(worksheet="financas_gerais", data=edited_df)
            st.success("Atualizado!")
            st.rerun()
    else:
        st.warning("🔒 Modo Leitura: Não tens permissão para editar estas despesas.")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")

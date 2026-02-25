import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestão Pessoal", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)
st.title(f"👤 Gestão de Registos: {st.session_state.username}")

try:
    df_full = conn.read(worksheet="financas_individuais", ttl=0)
    admin_access = st.session_state.perfil in ["Master", "Admin"]

    if admin_access:
        st.info("🔓 Gestão Total (Miguel/Raquel)")
        edited_ind = st.data_editor(df_full, num_rows="dynamic", use_container_width=True)
    else:
        # Gabriel vê apenas os seus, pode criar novos, mas não editar/apagar os antigos
        df_view = df_full[df_full["User_ID"] == st.session_state.username]
        st.info("📝 Podes adicionar novos registos pessoais abaixo.")
        edited_ind_parcial = st.data_editor(df_view, num_rows="dynamic", use_container_width=True,
                                           disabled=df_view.columns)
        
        # Para o Gabriel, precisamos de juntar o que ele criou com a base total para não apagar os outros
        if st.button("💾 Guardar os meus registos"):
            df_final = pd.concat([df_full[df_full["User_ID"] != st.session_state.username], edited_ind_parcial])
            conn.update(worksheet="financas_individuais", data=df_final)
            st.success("✅ Guardado!")
            st.rerun()
        st.stop() # Interrompe aqui para o Gabriel não usar o botão de admin

    if st.button("💾 Confirmar Alterações (Master)"):
        conn.update(worksheet="financas_individuais", data=edited_ind)
        st.success("✅ Base de dados atualizada!")
        st.rerun()

except Exception as e:
    st.error(f"Erro: {e}")

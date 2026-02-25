import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Gestão Pessoal", page_icon="👤")

# Proteção de Login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Por favor, faça login na página principal.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

st.title(f"👤 Gestão Pessoal: {st.session_state.username}")

try:
    # 1. Leitura dos dados
    df_ind = conn.read(worksheet="financas_individuais", ttl=0)
    
    # Limpeza de nomes de colunas para evitar erros de espaços
    df_ind.columns = df_ind.columns.str.strip()

    # 2. Verificação da Coluna de Filtro
    # Vamos verificar se a coluna se chama 'utilizador' ou 'nome'
    coluna_filtro = None
    for col in ["utilizador", "nome", "User"]:
        if col in df_ind.columns:
            coluna_filtro = col
            break

    if coluna_filtro:
        meus_dados = df_ind[df_ind[coluna_filtro] == st.session_state.username]
        
        if meus_dados.empty:
            st.info(f"Olá {st.session_state.username}, ainda não tens registos nesta tabela.")
        else:
            st.subheader("Os teus registos")
            st.dataframe(meus_dados, use_container_width=True)
    else:
        st.error("❌ Erro de Estrutura: A aba 'financas_individuais' precisa de uma coluna chamada 'utilizador'.")
        st.info("Colunas atuais encontradas: " + ", ".join(df_ind.columns))

except Exception as e:
    st.error("Aba 'financas_individuais' não encontrada ou vazia.")
    st.info("Certifica-te de que criaste a aba e adicionaste pelo menos a primeira linha com os títulos das colunas.")

st.divider()

# 3. Formulário de Inserção Simples
with st.form("novo_registo_pessoal"):
    st.write("### ➕ Adicionar Novo Registo")
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0, step=0.01)
    
    if st.form_submit_button("Guardar"):
        # Criar nova linha (ajusta os nomes das colunas conforme o teu Sheets)
        nova_linha = pd.DataFrame([{
            "utilizador": st.session_state.username,
            "descricao": desc,
            "valor": valor
        }])
        
        # Aqui podes adicionar a lógica de concatenação e conn.update se a aba já existir
        st.success("Dados prontos para gravar! (Verifica se as colunas no Sheets batem certo com estas)")

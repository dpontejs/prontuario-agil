import streamlit as st
import sys, os
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import execute_read, execute_query

st.set_page_config(page_title="Pacientes", page_icon="👤", layout="wide")
st.title("Gestão de Pacientes")

tab_listar, tab_inserir = st.tabs(["Listar", "Inserir"])

with tab_inserir:
    with st.form("form_paciente"):
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF", placeholder="000.000.000-00")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        data_nasc = st.date_input(
            "Data de Nascimento",
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )
        submitted = st.form_submit_button("Cadastrar")

        if submitted and nome and cpf:
            try:
                execute_query(
                    "INSERT INTO paciente (nome, cpf, email, telefone, data_nascimento) VALUES (%s, %s, %s, %s, %s)",
                    (nome, cpf, email, telefone, data_nasc),
                )
                st.success(f"Paciente '{nome}' cadastrado!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")

with tab_listar:
    pacientes = execute_read("SELECT * FROM paciente ORDER BY nome")

    if not pacientes:
        st.info("Nenhum paciente cadastrado.")
    else:
        for p in pacientes:
            with st.expander(f"{p['nome']} — CPF: {p['cpf']}"):
                col1, col2 = st.columns(2)
                with col1:
                    novo_nome = st.text_input("Nome", value=p["nome"], key=f"nome_{p['id']}")
                    novo_email = st.text_input("Email", value=p["email"] or "", key=f"email_{p['id']}")
                    novo_tel = st.text_input("Telefone", value=p["telefone"] or "", key=f"tel_{p['id']}")
                with col2:
                    if st.button("Salvar alterações", key=f"save_{p['id']}"):
                        execute_query(
                            "UPDATE paciente SET nome=%s, email=%s, telefone=%s WHERE id=%s",
                            (novo_nome, novo_email, novo_tel, p["id"]),
                        )
                        st.success("Atualizado!")
                        st.rerun()
                    if st.button("Remover", key=f"del_{p['id']}", type="secondary"):
                        execute_query("DELETE FROM paciente WHERE id=%s", (p["id"],))
                        st.warning("Paciente removido.")
                        st.rerun()

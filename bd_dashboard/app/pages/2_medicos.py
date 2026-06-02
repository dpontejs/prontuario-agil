import streamlit as st
import sys, os
from datetime import datetime, timedelta, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import execute_read, execute_query

st.set_page_config(page_title="Médicos", page_icon="🩺", layout="wide")
st.title("Gestão de Médicos")

tab_listar, tab_inserir, tab_horarios = st.tabs(["Listar", "Inserir", "Horários Disponíveis"])

with tab_inserir:
    with st.form("form_medico"):
        nome = st.text_input("Nome")
        crm = st.text_input("CRM", placeholder="CRM-RN-0000")
        especialidade = st.text_input("Especialidade")
        submitted = st.form_submit_button("Cadastrar")

        if submitted and nome and crm and especialidade:
            try:
                execute_query(
                    "INSERT INTO medico (nome, crm, especialidade) VALUES (%s, %s, %s)",
                    (nome, crm, especialidade),
                )
                st.success(f"Médico '{nome}' cadastrado!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")

with tab_listar:
    medicos = execute_read("SELECT * FROM medico ORDER BY nome")

    if not medicos:
        st.info("Nenhum médico cadastrado.")
    else:
        for m in medicos:
            with st.expander(f"{m['nome']} — {m['especialidade']} ({m['crm']})"):
                col1, col2 = st.columns(2)
                with col1:
                    novo_nome = st.text_input("Nome", value=m["nome"], key=f"nome_{m['id']}")
                    nova_esp = st.text_input("Especialidade", value=m["especialidade"], key=f"esp_{m['id']}")
                with col2:
                    if st.button("Salvar alterações", key=f"save_{m['id']}"):
                        execute_query(
                            "UPDATE medico SET nome=%s, especialidade=%s WHERE id=%s",
                            (novo_nome, nova_esp, m["id"]),
                        )
                        st.success("Atualizado!")
                        st.rerun()
                    if st.button("Remover", key=f"del_{m['id']}", type="secondary"):
                        execute_query("DELETE FROM medico WHERE id=%s", (m["id"],))
                        st.warning("Médico removido.")
                        st.rerun()

with tab_horarios:
    st.subheader("Cadastrar Horários Disponíveis")
    medicos = execute_read("SELECT id, nome, especialidade FROM medico ORDER BY nome")

    if not medicos:
        st.warning("Cadastre médicos primeiro.")
    else:
        medico_sel = st.selectbox(
            "Médico",
            options=medicos,
            format_func=lambda m: f"{m['nome']} ({m['especialidade']})",
            key="medico_horario"
        )

        with st.form("form_horario"):
            data = st.date_input("Data")
            hora = st.time_input("Horário", value=time(9, 0))
            submitted = st.form_submit_button("Adicionar horário")

            if submitted:
                data_hora = datetime.combine(data, hora)
                try:
                    execute_query(
                        "INSERT INTO horario_disponivel (medico_id, data_hora, is_ocupado) VALUES (%s, %s, FALSE)",
                        (medico_sel["id"], data_hora),
                    )
                    st.success(f"Horário {data_hora.strftime('%d/%m/%Y %H:%M')} adicionado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        st.divider()
        st.subheader("Horários cadastrados")

        horarios = execute_read("""
            SELECT h.id, m.nome as medico, h.data_hora, h.is_ocupado
            FROM horario_disponivel h
            JOIN medico m ON h.medico_id = m.id
            WHERE h.medico_id = %s
            ORDER BY h.data_hora
        """, (medico_sel["id"],))

        if not horarios:
            st.info("Nenhum horário cadastrado para este médico.")
        else:
            for h in horarios:
                status = "🔴 Ocupado" if h["is_ocupado"] else "🟢 Livre"
                col1, col2 = st.columns([3, 1])
                col1.write(f"{h['data_hora'].strftime('%d/%m/%Y %H:%M')} — {status}")
                if col2.button("Remover", key=f"del_h_{h['id']}"):
                    execute_query("DELETE FROM horario_disponivel WHERE id=%s", (h["id"],))
                    st.rerun()

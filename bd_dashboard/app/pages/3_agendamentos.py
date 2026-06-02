import streamlit as st
import sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import execute_read, execute_query

st.set_page_config(page_title="Agendamentos", page_icon="📅", layout="wide")
st.title("Gestão de Agendamentos")

tab_listar, tab_inserir = st.tabs(["Listar", "Novo Agendamento"])

with tab_inserir:
    pacientes = execute_read("SELECT id, nome FROM paciente ORDER BY nome")
    medicos = execute_read("SELECT id, nome, especialidade FROM medico ORDER BY nome")

    if not pacientes or not medicos:
        st.warning("Cadastre pacientes e médicos antes de criar agendamentos.")
    else:
        medico_sel = st.selectbox(
            "Médico",
            options=medicos,
            format_func=lambda m: f"{m['nome']} ({m['especialidade']})",
            key="medico_novo"
        )

        horarios = []
        if medico_sel:
            horarios = execute_read(
                "SELECT id, data_hora FROM horario_disponivel WHERE medico_id = %s AND is_ocupado = FALSE ORDER BY data_hora",
                (medico_sel["id"],)
            )

        if not horarios:
            st.info("Nenhum horário disponível para este médico. Cadastre horários na página de Médicos.")
        else:
            with st.form("form_agendamento"):
                paciente_sel = st.selectbox(
                    "Paciente",
                    options=pacientes,
                    format_func=lambda p: p["nome"],
                )
                horario_sel = st.selectbox(
                    "Horário disponível",
                    options=horarios,
                    format_func=lambda h: h["data_hora"].strftime("%d/%m/%Y %H:%M"),
                )
                submitted = st.form_submit_button("Agendar")

                if submitted:
                    try:
                        execute_query(
                            "INSERT INTO agendamento (horario_id, paciente_id, status) VALUES (%s, %s, 'RESERVADO')",
                            (horario_sel["id"], paciente_sel["id"]),
                        )
                        execute_query(
                            "UPDATE horario_disponivel SET is_ocupado = TRUE WHERE id = %s",
                            (horario_sel["id"],)
                        )
                        st.success("Agendamento criado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

with tab_listar:
    filtro_status = st.selectbox("Filtrar por status", ["Todos", "RESERVADO", "CONFIRMADO", "CANCELADO"])

    sql = """
        SELECT a.id, p.nome as paciente, m.nome as medico, m.especialidade,
               h.data_hora, a.status
        FROM agendamento a
        JOIN paciente p ON a.paciente_id = p.id
        JOIN horario_disponivel h ON a.horario_id = h.id
        JOIN medico m ON h.medico_id = m.id
    """
    params = ()
    if filtro_status != "Todos":
        sql += " WHERE a.status = %s"
        params = (filtro_status,)
    sql += " ORDER BY h.data_hora DESC"

    agendamentos = execute_read(sql, params)

    if not agendamentos:
        st.info("Nenhum agendamento encontrado.")
    else:
        for a in agendamentos:
            status_icon = {"RESERVADO": "🟡", "CONFIRMADO": "🟢", "CANCELADO": "🔴"}.get(a["status"], "⚪")
            with st.expander(f"{status_icon} {a['paciente']} → {a['medico']} | {a['data_hora'].strftime('%d/%m/%Y %H:%M')}"):
                st.write(f"**Especialidade:** {a['especialidade']}")
                st.write(f"**Status:** {a['status']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if a["status"] == "RESERVADO" and st.button("Confirmar", key=f"conf_{a['id']}"):
                        execute_query("UPDATE agendamento SET status='CONFIRMADO' WHERE id=%s", (a["id"],))
                        st.rerun()
                with col2:
                    if a["status"] != "CANCELADO" and st.button("Cancelar", key=f"canc_{a['id']}"):
                        execute_query("UPDATE agendamento SET status='CANCELADO' WHERE id=%s", (a["id"],))
                        execute_query(
                            "UPDATE horario_disponivel SET is_ocupado=FALSE WHERE id=(SELECT horario_id FROM agendamento WHERE id=%s)",
                            (a["id"],)
                        )
                        st.rerun()
                with col3:
                    if st.button("Remover", key=f"del_{a['id']}", type="secondary"):
                        execute_query(
                            "UPDATE horario_disponivel SET is_ocupado=FALSE WHERE id=(SELECT horario_id FROM agendamento WHERE id=%s)",
                            (a["id"],)
                        )
                        execute_query("DELETE FROM agendamento WHERE id=%s", (a["id"],))
                        st.rerun()

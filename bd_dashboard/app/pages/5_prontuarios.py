import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import execute_read, execute_query

st.set_page_config(page_title="Prontuários", page_icon="📋", layout="wide")
st.title("Gestão de Prontuários")

tab_listar, tab_inserir = st.tabs(["Listar", "Novo Prontuário"])

with tab_inserir:
    pacientes = execute_read("SELECT id, nome FROM paciente ORDER BY nome")
    medicos = execute_read("SELECT id, nome, especialidade FROM medico ORDER BY nome")

    if not pacientes or not medicos:
        st.warning("Cadastre pacientes e médicos antes de criar prontuários.")
    else:
        with st.form("form_prontuario"):
            paciente_sel = st.selectbox("Paciente", options=pacientes, format_func=lambda p: p["nome"])
            medico_sel = st.selectbox(
                "Médico",
                options=medicos,
                format_func=lambda m: f"{m['nome']} ({m['especialidade']})",
            )
            notas = st.text_area("Notas Clínicas")
            diagnostico = st.text_area("Diagnóstico")
            prescricao = st.text_area("Prescrição")
            submitted = st.form_submit_button("Registrar Prontuário")

            if submitted and paciente_sel and medico_sel:
                try:
                    execute_query(
                        """INSERT INTO prontuario
                           (paciente_id, medico_id, notas_clinicas, diagnostico, prescricao, finalizado)
                           VALUES (%s, %s, %s, %s, %s, FALSE)""",
                        (paciente_sel["id"], medico_sel["id"], notas, diagnostico, prescricao),
                    )
                    st.success("Prontuário registrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab_listar:
    prontuarios = execute_read("""
        SELECT pr.id, p.nome as paciente, m.nome as medico, m.especialidade,
               pr.notas_clinicas, pr.diagnostico, pr.prescricao,
               pr.data_registro, pr.finalizado
        FROM prontuario pr
        JOIN paciente p ON pr.paciente_id = p.id
        JOIN medico m ON pr.medico_id = m.id
        ORDER BY pr.data_registro DESC
    """)

    if not prontuarios:
        st.info("Nenhum prontuário registrado.")
    else:
        for pr in prontuarios:
            status = "🔒 Finalizado" if pr["finalizado"] else "✏️ Em aberto"
            with st.expander(f"{status} — {pr['paciente']} | {pr['medico']} | {pr['data_registro'].strftime('%d/%m/%Y %H:%M')}"):
                st.write(f"**Especialidade:** {pr['especialidade']}")

                if pr["finalizado"]:
                    st.write(f"**Notas Clínicas:** {pr['notas_clinicas']}")
                    st.write(f"**Diagnóstico:** {pr['diagnostico']}")
                    st.write(f"**Prescrição:** {pr['prescricao']}")
                    if st.button("Remover", key=f"del_{pr['id']}", type="secondary"):
                        execute_query("DELETE FROM prontuario WHERE id=%s", (pr["id"],))
                        st.rerun()
                else:
                    notas = st.text_area("Notas Clínicas", value=pr["notas_clinicas"] or "", key=f"notas_{pr['id']}")
                    diag = st.text_area("Diagnóstico", value=pr["diagnostico"] or "", key=f"diag_{pr['id']}")
                    presc = st.text_area("Prescrição", value=pr["prescricao"] or "", key=f"presc_{pr['id']}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Salvar", key=f"save_{pr['id']}"):
                            execute_query(
                                "UPDATE prontuario SET notas_clinicas=%s, diagnostico=%s, prescricao=%s WHERE id=%s",
                                (notas, diag, presc, pr["id"]),
                            )
                            st.success("Salvo!")
                            st.rerun()
                    with col2:
                        if st.button("Finalizar", key=f"fin_{pr['id']}"):
                            execute_query(
                                "UPDATE prontuario SET notas_clinicas=%s, diagnostico=%s, prescricao=%s, finalizado=TRUE WHERE id=%s",
                                (notas, diag, presc, pr["id"]),
                            )
                            st.success("Prontuário finalizado!")
                            st.rerun()
                    with col3:
                        if st.button("Remover", key=f"del_{pr['id']}", type="secondary"):
                            execute_query("DELETE FROM prontuario WHERE id=%s", (pr["id"],))
                            st.rerun()

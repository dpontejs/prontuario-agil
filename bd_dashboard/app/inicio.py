import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection, execute_read

st.set_page_config(
    page_title="Prontuário Ágil - Dashboard",
    page_icon="🏥",
    layout="wide",
)

st.title("Prontuário Ágil — Dashboard de Gestão")
st.markdown("Sistema de gestão de clínica médica com análise de dados públicos do CNES/DataSUS.")

st.divider()

try:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
    st.success("Conectado ao banco de dados MySQL")
except Exception as e:
    st.error(f"Erro ao conectar ao banco: {e}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pacientes = execute_read("SELECT COUNT(*) as total FROM paciente")[0]["total"]
    st.metric("Pacientes", total_pacientes)

with col2:
    total_medicos = execute_read("SELECT COUNT(*) as total FROM medico")[0]["total"]
    st.metric("Médicos", total_medicos)

with col3:
    total_agendamentos = execute_read("SELECT COUNT(*) as total FROM agendamento WHERE status != 'CANCELADO'")[0]["total"]
    st.metric("Agendamentos Ativos", total_agendamentos)

with col4:
    total_prontuarios = execute_read("SELECT COUNT(*) as total FROM prontuario")[0]["total"]
    st.metric("Prontuários", total_prontuarios)

st.divider()
st.markdown("### Navegação")
st.markdown("""
Use o menu lateral para acessar:
- **Pacientes** — Cadastro e gestão de pacientes
- **Médicos** — Cadastro, gestão e horários disponíveis
- **Agendamentos** — Reserva e confirmação de consultas
- **Prontuários** — Registro clínico dos atendimentos
- **Análise CNES** — Dados públicos e estatísticas
""")

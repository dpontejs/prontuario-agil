# Integração BD — Dashboard Prontuário Ágil

Este documento resume onde encontrar a entrega de Banco de Dados dentro do repositório principal.

## Local do código

O dashboard com integração ao MySQL está em `bd_dashboard/`.

- `bd_dashboard/sql/01_create_tables.sql`: criação das tabelas relacionais.
- `bd_dashboard/sql/02_create_views.sql`: criação da view analítica.
- `bd_dashboard/sql/03_seed_data.sql`: dados fictícios iniciais do domínio da clínica.
- `bd_dashboard/scripts/import_csv.py`: importação dos CSVs públicos do CNES/DataSUS.
- `bd_dashboard/app/`: frontend Streamlit com CRUD e análises.

## Dados reais

A base pública utilizada é o CNES/DataSUS, competência abril/2026, filtrada para o Rio Grande do Norte. O script importa estabelecimentos de saúde e vínculos profissionais, incluindo tipo de estabelecimento, município, CBO/especialidade e carga horária ambulatorial.

## Modelo relacional

Tabelas do domínio do Prontuário Ágil:

- `medico(id, nome, crm, especialidade)`
- `paciente(id, nome, cpf, email, telefone, data_nascimento)`
- `horario_disponivel(id, medico_id, data_hora, is_ocupado)`
- `agendamento(id, horario_id, paciente_id, status, data_criacao)`
- `prontuario(id, paciente_id, medico_id, notas_clinicas, diagnostico, prescricao, data_registro, finalizado)`

Tabelas de dados públicos:

- `estabelecimento_cnes(id, cnes_codigo, nome_fantasia, tipo_estabelecimento, uf, municipio)`
- `profissional_cnes(id, estabelecimento_cnes_id, nome, cbo, carga_horaria)`

View:

- `vw_estatisticas_especialidade`: agrega profissionais por CBO/especialidade usando `COUNT`, `AVG`, `MAX`, `MIN` e `SUM` sobre carga horária.

## Operações do dashboard

O dashboard implementa inserção, consulta, atualização e remoção de pacientes, médicos, horários, agendamentos e prontuários. Também exibe análises dos dados reais do CNES com gráficos e tabelas, respondendo perguntas sobre distribuição de estabelecimentos, concentração de profissionais, carga horária e especialidades prioritárias.

## Execução

```bash
cd bd_dashboard
./setup.sh
source venv/bin/activate
streamlit run app/inicio.py
```

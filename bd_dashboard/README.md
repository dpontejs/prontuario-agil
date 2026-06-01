# Dashboard BD — Prontuário Ágil

Módulo da avaliação de Banco de Dados integrado ao repositório principal do Prontuário Ágil. O dashboard usa MySQL como backend de dados e Streamlit como frontend para consulta, análise e manipulação dos dados.

## O que está incluído

- Tabelas de domínio do Prontuário Ágil: `medico`, `paciente`, `horario_disponivel`, `agendamento` e `prontuario`.
- Tabelas de dados públicos CNES/DataSUS: `estabelecimento_cnes` e `profissional_cnes`.
- View analítica: `vw_estatisticas_especialidade`.
- CRUD no dashboard para pacientes, médicos, horários, agendamentos e prontuários.
- Análises estatísticas com dados reais do CNES/DataSUS do Rio Grande do Norte, competência abril/2026.

## Setup rápido

Pré-requisitos: Docker, Docker Compose e Python 3.10+.

```bash
cd bd_dashboard
./setup.sh
```

Depois acesse o dashboard:

```bash
cd bd_dashboard
source venv/bin/activate
streamlit run app/inicio.py
```

URL local padrão: http://localhost:8501

## Dados públicos CNES

Fonte: CNES/DataSUS, Ministério da Saúde. O arquivo usado é `BASE_DE_DADOS_CNES_202604.ZIP`.

Download:

```text
https://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_202604.ZIP
```

Extraia o ZIP em:

```text
bd_dashboard/data/cnes/BASE_DE_DADOS_CNES_202604/
```

Depois importe:

```bash
cd bd_dashboard
source venv/bin/activate
python scripts/import_csv.py
```

Os arquivos CSV e o ZIP não são versionados porque são grandes e podem ser baixados da fonte pública.

## Estrutura

```text
bd_dashboard/
├── app/                 # Dashboard Streamlit
├── scripts/             # Seed e importação dos CSVs CNES
├── sql/                 # Tabelas, view e dados fictícios iniciais
├── docker-compose.yml   # MySQL 8 local
├── requirements.txt     # Dependências do dashboard
└── setup.sh             # Setup automatizado
```

## Integração com o projeto principal

A integração exigida para a entrega está neste módulo: o frontend `app/` conecta ao backend MySQL configurado em `docker-compose.yml`, executa consultas SQL, manipula registros do domínio do Prontuário Ágil e exibe análises dos dados públicos CNES. O projeto Django existente continua separado como MVP de Engenharia de Software e não precisa ser alterado para executar esta entrega de BD.

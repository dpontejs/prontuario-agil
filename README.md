# Prontuário Ágil

**Sistema web para gestão de clínicas médicas** — agendamento autônomo de consultas e prontuário eletrônico para médicos.

> Projeto desenvolvido na disciplina de Engenharia de Software — UFRN  
> Equipe: Diego Ponte, Ankier, Célio, Guilherme

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Requisitos](#requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Executar](#como-executar)
- [Autenticação e Autorização](#autenticação-e-autorização)
- [Endpoints da API](#endpoints-da-api)
- [Testes e Cobertura](#testes-e-cobertura)
- [Integração Contínua](#integração-contínua)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Princípios e Padrões de Projeto](#princípios-e-padrões-de-projeto)
- [Diagramas](#diagramas)
- [Dashboard de Banco de Dados](#dashboard-de-banco-de-dados)
- [Licença](#licença)

---

## Sobre o Projeto

O **Prontuário Ágil** resolve um problema real identificado nos dados públicos do CNES/DataSUS (RN, abril/2026): má distribuição de profissionais de saúde e dificuldade de agendamento em clínicas. O sistema oferece:

- **Área do paciente:** busca médicos por especialidade, agenda e cancela consultas.
- **Área do médico:** registra prontuários clínicos (notas, diagnóstico, prescrição) com controle de finalização.
- **API REST protegida por JWT** com controle de acesso por papel (médico/paciente).
- **Dashboard analítico** com dados reais do CNES/DataSUS para visualização de métricas de saúde pública.

---

## Requisitos

- Python 3.10+
- pip
- SQLite (padrão) ou MySQL 8.0+ (opcional, via variáveis de ambiente)
- Para o dashboard: Docker (MySQL) + Streamlit

---

## Instalação e Configuração

```bash
# 1. Clonar o repositório
git clone https://github.com/dpontejs/prontuario-agil.git
cd prontuario-agil

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Aplicar migrações
python manage.py migrate

# 5. Criar usuário padrão do sistema (username: super / senha: 12345678)
python manage.py criar_usuario_padrao

# 6. (Opcional) Popular o banco com dados de demonstração
#    Cria usuários medico/paciente e dados pré-cadastrados para apresentação
python manage.py popular_banco
```

### Variáveis de ambiente (opcional — MySQL)

Crie um arquivo `.env` na raiz ou exporte as variáveis:

```bash
DB_ENGINE=django.db.backends.mysql
DB_NAME=prontuario_db
DB_USER=root
DB_PASSWORD=senha
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=sua-chave-secreta
DEBUG=False
```

---

## Como Executar

### API + Front-end

```bash
python manage.py runserver
```

Acesse em `http://localhost:8000/`:

| URL | Descrição | Acesso |
|---|---|---|
| `/` | Página inicial | JWT (médico ou paciente) |
| `/login/` | Login com JWT | Pública |
| `/agendar/` | Buscar médicos e agendar | JWT — apenas paciente |
| `/meus-agendamentos/` | Ver e cancelar agendamentos | JWT — apenas paciente |
| `/prontuario/` | Registrar prontuários clínicos | JWT — apenas médico |
| `/api/` | DRF Browsable API | JWT |
| `/admin/` | Django Admin | Superuser |

### Dashboard de Banco de Dados

```bash
cd bd_dashboard
./setup.sh
source venv/bin/activate
streamlit run app/inicio.py
```

Acesse em `http://localhost:8501/`.

---

## Autenticação e Autorização

O sistema usa **JWT (JSON Web Token)** via `djangorestframework-simplejwt`.

### Obter token de acesso

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_usuario", "password": "sua_senha"}'
```

Resposta:
```json
{ "access": "eyJ...", "refresh": "eyJ..." }
```

### Usar o token em requisições protegidas

```bash
curl http://localhost:8000/api/medicos/ \
  -H "Authorization: Bearer eyJ..."
```

### Papéis (Autorização)

| Papel | Como configurar | Acesso |
|---|---|---|
| **Superuser** | `python manage.py criar_usuario_padrao` | Somente `/admin/` |
| **Médico** | Vincular `User` a um `Medico` via `/admin/` | Prontuários + leitura geral |
| **Paciente** | Vincular `User` a um `Paciente` via `/admin/` | Agendar, cancelar, listar horários |
| Sem token | — | 401 em todos os endpoints `/api/` |
| Token sem papel Médico | — | 403 em `POST /api/prontuarios/` |

> **Demo rápida:** após `python manage.py popular_banco` os usuários `medico` e `paciente` (senha `12345678`) já estão vinculados aos papéis corretos.

---

## Endpoints da API

| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| `POST` | `/api/token/` | Login — retorna access + refresh token | Pública |
| `POST` | `/api/token/refresh/` | Renova o token de acesso | Pública |
| `GET` | `/api/medicos/` | Lista médicos (filtro: `?especialidade=`) | JWT |
| `GET` | `/api/horarios/` | Lista horários (filtro: `?medico=&disponivel=true`) | JWT |
| `POST` | `/api/agendamentos/` | Reserva um horário (US01) | JWT |
| `POST` | `/api/agendamentos/{id}/cancelar/` | Cancela agendamento (US02) | JWT |
| `POST` | `/api/agendamentos/{id}/confirmar/` | Confirma agendamento (médico) | JWT |
| `GET` | `/api/me/` | Perfil do usuário autenticado (papel, ids) | JWT |
| `GET` | `/api/agendamentos/` | Lista agendamentos | JWT |
| `GET` | `/api/pacientes/` | Lista pacientes | JWT |
| `POST` | `/api/prontuarios/` | Registra prontuário (US03) | JWT + IsMedico |
| `GET` | `/api/prontuarios/` | Lista prontuários | JWT + IsMedico |

---

## Testes e Cobertura

```bash
# Rodar todos os testes
python manage.py test agendamento

# Com relatório de cobertura
coverage run --source='agendamento' manage.py test agendamento
coverage report -m
```

**Resultado atual:** 21 testes, **90% de cobertura** (meta mínima: 60%).

```
Name                         Stmts   Miss  Cover
------------------------------------------------
agendamento/models.py           31      0   100%
agendamento/services.py         69     28    59%
agendamento/views.py            65     13    80%
agendamento/permissions.py       7      1    86%
agendamento/serializers.py      36      0   100%
...
TOTAL                          448     47    90%
```

Os testes cobrem:
- Reserva de horário (sucesso e horário ocupado)
- Cancelamento de agendamento (libera horário)
- Registro de prontuário por médico (201) e por não-médico (403)
- Edição de prontuário finalizado (400)
- Acesso sem token (401)
- Restrições de modelo (CPF único, vínculos opcionais)

---

## Integração Contínua

GitHub Actions roda automaticamente em todo **push** e **pull request** para `main`:

1. **Test Django API** — sobe MySQL, instala dependências, executa testes com relatório de cobertura.
2. **Check Dashboard** — valida sintaxe e linting do Streamlit.

Ver `.github/workflows/ci.yml`.

---

## Estrutura do Projeto

```text
prontuario-agil/
├── agendamento/                  # App Django (MVP de Eng. de Software)
│   ├── models.py                 # Medico, Paciente, HorarioDisponivel, Agendamento, Prontuario
│   ├── services.py               # AgendamentoService (regras de negócio)
│   ├── serializers.py            # Serializers DRF
│   ├── views.py                  # ViewSets da API REST
│   ├── permissions.py            # IsMedico, IsPaciente
│   ├── urls.py                   # Rotas da API (/api/)
│   ├── web_views.py              # Views de página (front-end)
│   ├── web_urls.py               # Rotas do front-end (/)
│   ├── templates/agendamento/    # Templates HTML
│   ├── static/agendamento/       # CSS e JS
│   └── tests/                    # Testes unitários e de API
├── prontuario_project/           # Configuração do projeto Django
├── bd_dashboard/                 # Dashboard Streamlit + MySQL (entrega de BD)
│   ├── app/                      # Páginas Streamlit (CRUD + análise CNES)
│   └── sql/                      # Schema, views e seed data
├── docs/                         # Documentação técnica
│   ├── userStories.md            # 3 User Stories
│   ├── principios-projeto.md     # Princípios de projeto (SOLID, DRY)
│   ├── padroes-projeto.md        # Padrões de projeto utilizados
│   ├── diagramas.md              # Diagramas estruturais e comportamentais
│   └── bd-modelagem.md           # Modelo ER do banco de dados
├── .github/workflows/ci.yml      # CI — GitHub Actions
├── manage.py
└── requirements.txt
```

---

## Princípios e Padrões de Projeto

- [Princípios de Projeto](docs/principios-projeto.md) — SRP, DRY, Separação de Responsabilidades (obrigatório)
- [Padrões de Projeto](docs/padroes-projeto.md) — Service Layer, Serializer/DTO, ViewSet+Router (extra)
- [Diagramas](docs/diagramas.md) — Casos de uso, classes, sequência, estados (extra)

---

## Dashboard de Banco de Dados

A entrega de Banco de Dados está em [`bd_dashboard/`](bd_dashboard/README.md):

- Schema relacional MySQL com 7 tabelas e 1 view analítica.
- Dados reais importados do CNES/DataSUS (RN, abril/2026).
- Dashboard Streamlit com CRUD completo e análises estatísticas.

---

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo `LICENSE`.

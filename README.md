# Eng-de-Software-UFRN

## Índice

- [Eng-de-Software-UFRN](#eng-de-software-ufrn)
  - [Índice](#índice)
  - [Sobre o Projeto](#sobre-o-projeto)
    - [Título](#título)
    - [Descrição](#descrição)
    - [Componentes](#componentes)
  - [Como clonar ou baixar](#como-clonar-ou-baixar)
    - [Clonar via HTTPS](#clonar-via-https)
    - [Clonar via SSH](#clonar-via-ssh)
    - [Baixar como ZIP](#baixar-como-zip)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Licença](#licença)

## Sobre o Projeto

### Título
Prontuário Ágil

### Descrição
O projeto consiste no desenvolvimento de um sistema web para gestão de clínicas médicas, estruturado em dois módulos principais: um ambiente de agendamento autônomo para pacientes e uma área restrita para médicos gerenciarem prontuários eletrônicos e históricos clínicos.

### Componentes
- Diego Ponte
- Ankier
- Célio
- Guilherme

## Como clonar ou baixar

Você pode obter este repositório de três formas:

### Clonar via HTTPS

```bash
git clone https://github.com/dpontejs/prontuario-agil.git
```

Isso criará uma cópia local do repositório em sua máquina.

### Clonar via SSH

Se você já configurou sua chave SSH no GitHub, pode clonar usando:

```bash
git clone git@github.com:dpontejs/prontuario-agil.git
```

Isso criará uma cópia local do repositório em sua máquina.

### Baixar como ZIP

1. Acesse a página do repositório no GitHub:
   [https://github.com/dpontejs/prontuario-agil](https://github.com/dpontejs/prontuario-agil)
2. Clique no botão **Code** (verde).
3. Selecione **Download ZIP**.
4. Extraia o arquivo ZIP para o local desejado em seu computador.


## Dashboard de Banco de Dados

A entrega da Unidade 2 de Banco de Dados está integrada a este repositório no diretório [`bd_dashboard/`](bd_dashboard/README.md).

Esse módulo contém o dashboard Streamlit do Prontuário Ágil integrado a um banco MySQL, com scripts SQL, carga de dados fictícios do domínio da clínica, importação de dados públicos CNES/DataSUS e análises estatísticas para a apresentação.

Execução resumida:

```bash
cd bd_dashboard
./setup.sh
source venv/bin/activate
streamlit run app/inicio.py
```

Mais detalhes estão em [`docs/bd-dashboard.md`](docs/bd-dashboard.md).

## Estrutura do Projeto

```text
prontuario-agil/
├── agendamento/             # App Django do MVP de Engenharia de Software
├── prontuario_project/      # Configuração do projeto Django
├── bd_dashboard/            # Dashboard Streamlit + MySQL da entrega de BD
├── docs/                    # Documentação do projeto e da integração de BD
├── manage.py
├── README.md
└── LICENSE
```

- `agendamento/`: models, services e testes do fluxo de agendamento.
- `bd_dashboard/`: tabelas SQL, importação CNES/DataSUS e dashboard com CRUD/análises.
- `docs/bd-dashboard.md`: resumo da integração BD para a entrega.

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo `LICENSE` para mais detalhes.

# Avaliação de Unidade 2 – Modelagem e Integração com Dados Públicos


### Objetivo:

O objetivo deste trabalho é aplicar conceitos de modelagem e consulta em bancos de dados relacionais (MySQL), e análise de dados a partir de dados públicos. Além de exercitar a manipulação e organização de dados, os alunos deverão explorar formas de visualização e integração com aplicações frontend.


### Descrição das Atividades:

1. Criação das Tabelas: Crie pelo menos 3 tabelas (uma delas pode ser uma view) com dados (podem ser fictícios), como banco de dados do projeto da disciplina de Engenharia de Software. Essas tabelas devem ser baseadas num modelo Entidade-Relacionamento proposto, que deve ser transformado em relações. Esse banco de dados deve estar integrado ao projeto de EngSoftware, de modo que resultados das consultas e manipulação dos dados devem ser integrados a um Dashboard (frontend) desenvolvido em qualquer linguagem de programação à escolha do grupo, com integração ao banco de dados MySQL. Exemplos de tecnologias que podem ser utilizadas:

    Python (com a biblioteca mysql.connector e frameworks como Streamlit ou Dash),
    Java (via API JDBC),
    ou outras linguagens e ferramentas equivalentes.

 2. Escolha de Tema: Cada grupo deverá selecionar um tema de interesse para análise (por exemplo: saúde, finanças, educação, tecnologia, transporte, meio ambiente), que deve estar relacionado ao projeto da disciplina de Engenharia de Software, de forma a validar hipóteses, justificar a importância do projeto ou enriquecer a discussão da solução proposta. Os grupos deverão buscar dados em fontes públicas confiáveis (exemplo: dados.gov.br).

É necessário utilizar pelo menos um conjunto de dados em formato .csv.

Os dados deverão ser importados para o MySQL, criando as tabelas correspondentes no banco.


### Apresentação em Sala:

1. Análise de dados: realizar alguma análise estatística relevante para o seu projeto a partir dos dados reais, por exemplo através das funções MAX, MIN, SUM, AVG. Tal análise não precisa estar no frontend, e pode ser exibida no próprio banco de dados (porém, apresentações em dashboard são bem-vindas). As consultas devem gerar informações úteis relacionadas ao tema do trabalho e alinhadas com os objetivos do projeto.

2. Modelagen: Deve ser mostrado o modelo ER, as relações e as tabelas/views criadas no BD.

3. BD em prática: Deve ser mostrado operações de consulta, inserção, remoção e alteração dos dados do BD através do Dashboard (frontend).

As apresentações ocorrerão todas no dia 03/06, com 15 min por grupo.


### Entrega:

Um relatório em PDF de até 2000 palavras (considerando o texto escrito) contendo

    - Apresentação do projeto e componentes do grupo.
    - Descrição dos dados reais utilizados e sua origem.
    - Análise dos dados: o contexto do problema estudado e as perguntas respondidas - pelos dados reais.
    - Imagens do Dashboard e seu funcionamento
    - Link do projeto do GitHub, com indicação de onde encontrar o(s) código(s) do - dashboard com integração ao BD.
    - O modelo ER, as relações e as tabelas/views criadas no BD.
    - Explicação das tabelas/views criadas, e dos tipos de consultas e manipulações nos dados implementadas.
    - A descrição do processo de integração entre o backend (MySQL) e o frontend (dashboard).



Critérios de Avaliação:

    -Correção técnica na modelagem das tabelas e importação dos dados.
    - Capacidade de análise e interpretação dos resultados obtidos.
    - Pertinência e utilidade das tabelas/views criadas, das consultas e manipulação dos dados em relação ao projeto.
    - Funcionamento correto da integração entre o MySQL e o dashboard.
    - Clareza e organização do relatório entregue.
    - Qualidade da apresentação oral do trabalho.

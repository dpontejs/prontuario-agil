# Relatório de Execução de Testes - Prontuário Ágil

Este documento detalha os testes de unidade realizados na Sprint 2 para validar as regras de negócio do MVP. Por decisões de alinhamento técnico da equipe, a arquitetura utilizada foi modificada para Python utilizando o framework **Django**.

## Classe/Módulo Testado
* **Arquivo:** `agendamento/services.py`
* **Classe:** `AgendamentoService`
* **Camada:** Services (Camada de Regras de Negócio isolada)

## Cenários de Teste Implementados
1. **`test_deve_reservar_horario_com_sucesso`**: Garante que, ao solicitar um horário livre válido, o sistema cria o agendamento com status `RESERVADO` e altera o estado do horário para ocupado.
2. **`test_deve_lancar_erro_se_horario_ja_estiver_ocupado`**: Valida a regra de negócio que impede agendamentos duplicados. Se o horário já constar como ocupado, o sistema lança uma exceção `ValidationError`.

## Resultado da Cobertura de Código
A ferramenta utilizada para medição foi o pacote `coverage` do Python. A meta de 60% estipulada foi amplamente superada, atingindo **86%** de cobertura específica no arquivo de regras de negócio e **95%** de cobertura total no módulo de agendamento.

Abaixo consta a evidência do terminal de testes:

Name                                     Stmts   Miss  Cover
------------------------------------------------------------
agendamento\__init__.py                      0      0   100%
agendamento\admin.py                         1      0   100%
agendamento\apps.py                          4      0   100%
agendamento\migrations\0001_initial.py       6      0   100%
agendamento\migrations\__init__.py           0      0   100%
agendamento\models.py                       14      0   100%
agendamento\services.py                     14      2    86%
agendamento\tests.py                        19      0   100%
agendamento\views.py                         1      1     0%
------------------------------------------------------------
TOTAL                                       59      3    95%
## US01: Agendamento de Consulta (Paciente)

* Descrição: Como paciente, eu quero escolher uma especialidade médica e um horário disponível para eu marcar uma consulta.

* Prioridade: Alta  
* Estimativa: 8 pontos   
* ( visto a complexidade de “travar”)

### Critérios de aceitação

1. O sistema deve listar os médicos de acordo com a especialidade escolhida.  
2. O sistema deve apresentar apenas horários que não possuam reserva ou agendamentos confirmados.  
3. Ao selecionar um horário o sistema deve “travar” o horário, para que não haja conflito com outro usuário marcando o mesmo espaço simultaneamente.  
4. O usuário deve receber uma confirmação por e-mail após a confirmação do agendamento.  
5. O tempo de “travar” deve ser de 10 minutos para expirar, caso o pagamento ou a confirmação final não seja realizada.

## US02: Cancelamento de consulta pelo paciente (Paciente)

* Descrição: Como paciente, eu quero cancelar uma consulta agendada pelo sistema, para que o horário seja liberado e eu não seja penalizado por faltas injustificadas.  
*  Prioridade: Média  
*  Estimativa: 3 pontos

### Critérios de Aceitação

1.  O paciente deve visualizar a lista de suas consultas futuras e ter a opção de cancelar cada uma.  
2.  O sistema deve impedir cancelamentos com menos de 2 horas de antecedência, exibindo mensagem explicativa.  
3.  Após o cancelamento, o horário deve ser liberado automaticamente na agenda do médico.  
4. O paciente e o médico devem receber uma notificação de confirmação do cancelamento.

## US03: Registo de de informações durante a consulta (Médico)

* Descrição: Como médico, eu quero registrar as informações do atendimento durante a consulta, para manter o histórico clínico do paciente atualizado.  
*  Prioridade: Alta  
*  Estimativa: 5 pontos

### Critérios de Aceitação

1.  O médico deve conseguir inserir notas clínicas, diagnósticos e prescrições.  
2.  O sistema deve salvar automaticamente a data e hora do registro.  
3.  Somente médicos autenticados e autorizados podem editar o prontuário.  
4.  O registro deve ser vinculado permanentemente ao CPF/cadastro do paciente.  
5. Após finalizar o atendimento, o registro médico não poderá ser editado, permitindo apenas adicionar informações extras através de adendo assinados. 
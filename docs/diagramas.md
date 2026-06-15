# Diagramas — Prontuário Ágil

Diagramas estruturais e comportamentais do sistema.

---

## Diagrama de Casos de Uso

```mermaid
graph TD
  subgraph Sistema["Prontuário Ágil"]
    UC1[Buscar médicos por especialidade]
    UC2[Reservar horário de consulta]
    UC3[Cancelar agendamento]
    UC4[Registrar prontuário clínico]
    UC5[Visualizar prontuários]
    UC6[Login JWT]
  end

  Paciente -->|US01| UC1
  Paciente -->|US01| UC2
  Paciente -->|US02| UC3
  Medico -->|US03| UC4
  Medico --> UC5
  Paciente --> UC6
  Medico --> UC6
```

---

## Diagrama de Classes

```mermaid
classDiagram
  class User {
    +username: str
    +password: str
  }

  class Medico {
    +user: User
    +nome: str
    +crm: str
    +especialidade: str
  }

  class Paciente {
    +user: User
    +nome: str
    +cpf: str
    +email: str
    +telefone: str
    +data_nascimento: date
  }

  class HorarioDisponivel {
    +medico: Medico
    +data_hora: datetime
    +is_ocupado: bool
  }

  class Agendamento {
    +horario: HorarioDisponivel
    +paciente_id: int
    +status: str
    +data_criacao: datetime
  }

  class Prontuario {
    +paciente: Paciente
    +medico: Medico
    +notas_clinicas: str
    +diagnostico: str
    +prescricao: str
    +data_registro: datetime
    +finalizado: bool
  }

  class AgendamentoService {
    +reservar_horario(horario_id, paciente_id) Agendamento
    +cancelar_agendamento(agendamento_id) Agendamento
    +registrar_prontuario(...) Prontuario
  }

  class IsMedico {
    +has_permission(request, view) bool
  }

  class IsPaciente {
    +has_permission(request, view) bool
  }

  User "1" --o "0..1" Medico : vincula
  User "1" --o "0..1" Paciente : vincula
  Medico "1" --> "0..*" HorarioDisponivel : possui
  HorarioDisponivel "1" --> "0..1" Agendamento : gera
  Paciente "1" --> "0..*" Prontuario : possui
  Medico "1" --> "0..*" Prontuario : registra
  AgendamentoService ..> Agendamento : cria/atualiza
  AgendamentoService ..> HorarioDisponivel : atualiza
  AgendamentoService ..> Prontuario : cria/atualiza
  IsMedico ..> Medico : verifica vínculo
  IsPaciente ..> Paciente : verifica vínculo
```

---

## Diagrama de Sequência — Reservar Horário (US01)

```mermaid
sequenceDiagram
  actor Paciente
  participant Frontend as Frontend (JS)
  participant API as Django View
  participant Service as AgendamentoService
  participant DB as Banco de Dados

  Paciente->>Frontend: Clica em "Agendar"
  Frontend->>API: POST /api/agendamentos/<br/>{ horario_id, paciente_id }<br/>Authorization: Bearer <token>

  API->>API: Valida JWT (IsAuthenticated)
  API->>API: Valida payload (ReservarHorarioSerializer)
  API->>Service: reservar_horario(horario_id, paciente_id)

  Service->>DB: SELECT ... FOR UPDATE (HorarioDisponivel)
  DB-->>Service: HorarioDisponivel

  alt Horário ocupado
    Service-->>API: ValidationError
    API-->>Frontend: 400 Bad Request
    Frontend-->>Paciente: "Horário já reservado"
  else Horário livre
    Service->>DB: UPDATE horario SET is_ocupado=True
    Service->>DB: INSERT INTO agendamento ...
    DB-->>Service: Agendamento criado
    Service-->>API: Agendamento
    API-->>Frontend: 201 Created { status: "RESERVADO" }
    Frontend-->>Paciente: "Consulta agendada com sucesso!"
  end
```

---

## Diagrama de Estados — Agendamento

```mermaid
stateDiagram-v2
  [*] --> RESERVADO : POST /api/agendamentos/\n(horário fica is_ocupado=True)

  RESERVADO --> CONFIRMADO : Confirmação manual\n(via admin ou endpoint futuro)
  RESERVADO --> CANCELADO : POST /api/agendamentos/{id}/cancelar/\n(horário volta is_ocupado=False)
  CONFIRMADO --> CANCELADO : Cancelamento tardio\n(regra: mín. 2h de antecedência — US02)

  CANCELADO --> [*]
  CONFIRMADO --> [*] : Consulta realizada
```

---

## Diagrama ER (Banco de Dados)

Ver [`docs/bd-modelagem.md`](bd-modelagem.md) para o diagrama ER completo com as tabelas do domínio e as tabelas CNES/DataSUS.

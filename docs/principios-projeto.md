# Princípios de Projeto — Prontuário Ágil

Este documento descreve os princípios de engenharia de software aplicados no desenvolvimento do MVP, com justificativa e apontamento de onde cada princípio se manifesta no código.

---

## 1. Princípio da Responsabilidade Única (SRP — SOLID)

**Definição:** Cada classe/módulo deve ter apenas uma razão para mudar.

**Onde:** `agendamento/services.py` — `AgendamentoService`

A camada de *services* concentra **apenas** as regras de negócio. Ela não sabe nada sobre HTTP, JSON ou banco de dados além do ORM:

```python
# agendamento/services.py — só sabe de regras de negócio
class AgendamentoService:
    @staticmethod
    def reservar_horario(horario_id, paciente_id):
        if horario.is_ocupado:
            raise ValidationError("Este horário já está reservado ou confirmado.")
        ...
```

Se as regras mudarem (ex.: adicionar limite de tempo para reserva), só `services.py` muda. Se o formato de resposta mudar, só `views.py` e `serializers.py` mudam. Cada arquivo tem uma única responsabilidade.

| Arquivo | Responsabilidade única |
|---|---|
| `models.py` | Estrutura dos dados e relacionamentos |
| `services.py` | Regras de negócio (reservar, cancelar, registrar prontuário) |
| `serializers.py` | Conversão entre objetos Python e JSON |
| `views.py` | Receber requisição HTTP e delegar ao service |
| `permissions.py` | Verificar autorização por papel |

---

## 2. Princípio Aberto/Fechado (OCP — SOLID)

**Definição:** Aberto para extensão, fechado para modificação.

**Onde:** `agendamento/permissions.py` e `agendamento/views.py`

As permissões são classes independentes (`IsMedico`, `IsPaciente`) que podem ser compostas nas views sem modificar o código existente:

```python
# agendamento/views.py
class ProntuarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsMedico]  # composição
```

Para adicionar um novo papel (ex.: `IsAdmin`), basta criar uma nova classe em `permissions.py` e compor nas views desejadas — sem alterar `IsMedico` ou `IsPaciente`.

---

## 3. Inversão de Dependência (DIP — SOLID)

**Onde:** Configuração do Django REST Framework em `prontuario_project/settings.py`

As views não instanciam autenticação diretamente — dependem da abstração configurada globalmente:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

Substituir JWT por outro mecanismo exigiria alterar apenas a configuração, sem tocar em nenhuma view.

---

## 4. DRY — Don't Repeat Yourself

**Definição:** Cada regra de negócio deve existir em um único lugar.

**Onde:** `agendamento/services.py` é a única fonte de verdade das regras.

A regra "horário ocupado não pode ser reservado" existe **uma vez**:

```python
# agendamento/services.py:24
if horario.is_ocupado:
    raise ValidationError("Este horário já está reservado ou confirmado.")
```

Essa mesma lógica é reutilizada pela API REST (via `views.py`) **e** pelos testes — sem duplicação. O view não reimplementa a regra; ele delega ao service.

---

## 5. Separação de Responsabilidades (Separation of Concerns)

**Onde:** Arquitetura em camadas do app `agendamento`

O sistema é dividido em camadas bem definidas:

```
Requisição HTTP
      ↓
  views.py  ← valida entrada via serializer
      ↓
 services.py ← aplica regra de negócio
      ↓
  models.py  ← persiste no banco via ORM
```

Cada camada faz **apenas o que é dela**. A view não acessa o banco diretamente; o service não formata JSON; o model não contém lógica de negócio.

---

## 6. Fail Fast (Falhe Cedo)

**Onde:** `agendamento/services.py` — validações explícitas com `ValidationError`

```python
# agendamento/services.py:9-10
except HorarioDisponivel.DoesNotExist:
    raise ValidationError("Horário não encontrado.") from None
```

O sistema falha imediatamente ao detectar um estado inválido, com mensagem clara, em vez de propagar o erro silenciosamente.

---

## 7. Atomicidade de Transações

**Onde:** `agendamento/services.py` — decorator `@transaction.atomic`

```python
@staticmethod
@transaction.atomic
def reservar_horario(horario_id, paciente_id):
    horario = HorarioDisponivel.objects.select_for_update().get(pk=horario_id)
    ...
```

O `@transaction.atomic` com `select_for_update()` garante que duas reservas simultâneas no mesmo horário não resultem em inconsistência — se qualquer operação falhar, tudo é revertido.

# Padrões de Projeto — Prontuário Ágil

Padrões identificados e aplicados no desenvolvimento do MVP.

---

## 1. Service Layer (Camada de Serviço)

**Categoria:** Arquitetural

**Onde:** `agendamento/services.py` — classe `AgendamentoService`

**O que é:** Uma camada intermediária entre as views (HTTP) e os models (banco de dados) que encapsula as regras de negócio.

**Por que foi usado:** Sem esta camada, as regras de negócio estariam espalhadas nas views (difícil de testar) ou nos models (viola SRP). Com o Service Layer, as regras são testáveis independentemente do HTTP e reutilizáveis por múltiplos pontos de entrada.

```python
# Regra de negócio encapsulada — testada diretamente, sem HTTP
class AgendamentoService:
    @staticmethod
    @transaction.atomic
    def reservar_horario(horario_id: int, paciente_id: int) -> Agendamento:
        ...
    
    @staticmethod
    @transaction.atomic
    def cancelar_agendamento(agendamento_id: int) -> Agendamento:
        ...
    
    @staticmethod
    @transaction.atomic
    def registrar_prontuario(...) -> Prontuario:
        ...
```

---

## 2. Data Transfer Object (DTO) via Serializers DRF

**Categoria:** Estrutural

**Onde:** `agendamento/serializers.py`

**O que é:** Objetos dedicados à transferência de dados entre camadas, com validação e transformação de formato (JSON ↔ Python).

**Por que foi usado:** Separar a lógica de validação/serialização da view e do model. Os serializers de entrada (`ReservarHorarioSerializer`, `RegistrarProntuarioSerializer`) têm apenas os campos necessários para a operação, sem expor a estrutura interna do model.

```python
# Serializer de entrada — valida e desacopla do model
class ReservarHorarioSerializer(serializers.Serializer):
    horario_id = serializers.IntegerField()
    paciente_id = serializers.IntegerField()

# Serializer de saída — controla o que é exposto na API
class AgendamentoSerializer(serializers.ModelSerializer):
    horario = HorarioDisponivelSerializer(read_only=True)
    class Meta:
        model = Agendamento
        fields = ["id", "horario", "paciente_id", "status", "data_criacao"]
```

---

## 3. ViewSet + Router (Command + Registry)

**Categoria:** Comportamental / Estrutural

**Onde:** `agendamento/views.py` + `agendamento/urls.py`

**O que é:** O `DefaultRouter` registra automaticamente as rotas CRUD a partir dos ViewSets, eliminando a configuração manual de cada URL.

**Por que foi usado:** Reduz boilerplate e garante consistência nas rotas (`/api/medicos/`, `/api/medicos/{id}/`). Ações adicionais (`cancelar`) são adicionadas via `@action` sem quebrar o padrão.

```python
# Registro declarativo de rotas
router = DefaultRouter()
router.register("medicos", MedicoViewSet, basename="medico")
router.register("agendamentos", AgendamentoViewSet, basename="agendamento")
```

---

## 4. Repository / Active Record (via ORM Django)

**Categoria:** Estrutural

**Onde:** `agendamento/models.py` + uso nos `services.py`

**O que é:** O ORM do Django implementa o padrão Active Record — cada model tem métodos para se salvar, buscar e deletar. O service atua como repositório ao chamar `objects.get()`, `objects.create()`, e `save(update_fields=[...])`.

**Por que foi usado:** Abstrai o SQL, garante portabilidade entre bancos (SQLite em desenvolvimento, MySQL em CI/produção) e simplifica as queries com o ORM expresivo do Django.

```python
# services.py — usa o ORM como repositório
horario = HorarioDisponivel.objects.select_for_update().get(pk=horario_id)
horario.is_ocupado = True
horario.save(update_fields=["is_ocupado"])  # UPDATE cirúrgico, não SELECT+UPDATE completo
```

---

## 5. Strategy (via Permissões DRF)

**Categoria:** Comportamental

**Onde:** `agendamento/permissions.py` + `agendamento/views.py`

**O que é:** Comportamentos de autorização intercambiáveis que podem ser compostos nas views.

**Por que foi usado:** Permite variar a estratégia de autorização por endpoint sem alterar o código das views. `IsMedico` e `IsPaciente` são estratégias independentes.

```python
# Cada view escolhe sua estratégia de autorização
class AgendamentoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]          # apenas autenticado

class ProntuarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsMedico]  # autenticado + papel médico
```

# Prompt para o Canva AI — Apresentação do Prontuário Ágil

Cole este prompt no Canva AI / Magic Design para gerar a apresentação acadêmica.

---

**Tema:** Apresentação acadêmica do projeto **"Prontuário Ágil"** — sistema web de gestão de clínicas médicas (agendamento autônomo de consultas + prontuário eletrônico). Disciplina de Engenharia de Software, UFRN. Equipe: Diego Ponte, Ankier, Célio, Guilherme.

**Estilo visual:** profissional e clean, área da saúde; paleta azul-petróleo + verde-água + branco; ícones de linha (estetoscópio, calendário, cadeado, gráfico); tipografia sans-serif legível; cada slide com título curto e poucos bullets; espaço para screenshots e diagramas. Idioma: português do Brasil. Cerca de **18–22 slides** para uma fala de **30–40 minutos**.

**Gere os slides nesta ordem:**

1. **Capa** — "Prontuário Ágil", subtítulo "Gestão inteligente de clínicas médicas", nomes da equipe, logo/ícone médico, UFRN.

2. **Agenda** — as 3 partes: Pitch, Parte Técnica, Demonstração.

3. **Contexto & Problema** — sobrecarga e má distribuição de profissionais na saúde pública; dificuldade de agendamento em clínicas.

4. **Problema baseado em dados (CNES/DataSUS, RN, abr/2026)** — destaque numérico: total de estabelecimentos, vínculos profissionais, média de profissionais por estabelecimento; espaço para gráfico "Top 10 estabelecimentos por equipe".

5. **A Solução / MVP** — Prontuário Ágil: agendamento autônomo para pacientes + prontuário eletrônico para médicos; proposta de valor em 3 bullets.

6. **Visão geral da arquitetura** — Django REST API + camada de Service + front-end Django Templates + Streamlit/MySQL (dashboard de dados); diagrama simples de camadas.

7. **Organização do repositório Git** — estrutura de pastas (`agendamento/`, `bd_dashboard/`, `docs/`) e estratégia de branches (main/dev/feat/*) com PRs e CI.

8. **User Story 01 — Agendar consulta (Paciente)** — descrição + critérios de aceitação (filtro por especialidade, "travar" horário, confirmação).

9. **User Story 02 — Cancelar consulta (Paciente)** — descrição + critérios (visualizar consultas futuras, restrição de 2h, liberação automática do horário).

10. **User Story 03 — Registrar prontuário (Médico)** — descrição + critérios (notas + diagnóstico + prescrição, acesso restrito a médicos, finalização imutável).

11. **Princípios de Projeto** — SRP (Service Layer), DRY (regra única no service), Separação de Responsabilidades (models/services/views/permissions); quadro com arquivo → responsabilidade.

12. **Autenticação & Autorização** — fluxo JWT (login → token → endpoint protegido); tabela de papéis (Paciente: 401→200, Médico: 403→201); diagrama de sequência do fluxo.

13. **Testes Unitários** — 21 testes, 90% de cobertura (meta 60%); tabela com nome do teste e o que valida; destaque para testes 401/403 (prova de autorização).

14. **Integração Contínua (CI)** — GitHub Actions: 2 jobs (Test Django API + Check Dashboard); rodado em todo push/PR; inclui relatório de cobertura; espaço para screenshot do badge verde.

15. **Demonstração — Roteiro** — passos: login na tela web, buscar médicos, agendar horário, meus agendamentos + cancelar, registrar prontuário (médico), tentativa sem permissão (403); espaço para screenshots.

16. **Contribuição de cada componente** — quem fez o quê: Diego (API REST, auth/JWT, CI), Ankier (?), Célio (?), Guilherme (?); preencher conforme divisão real da equipe.

17. **(Extra) Diagramas** — casos de uso (Paciente/Médico), diagrama de classes (models + service + permissions), diagrama de sequência (reservar horário), diagrama de estados do Agendamento; espaço para imagens renderizadas do Mermaid.

18. **(Extra) Padrões de Projeto** — Service Layer, Serializer/DTO (DRF), ViewSet+Router, Active Record (ORM Django), Strategy (permissões compostas); 1 bullet de justificativa por padrão.

19. **Conclusão** — resultados alcançados (API funcional, 90% cobertura, CI verde, front-end demo); aprendizados; próximos passos (notificação por e-mail US01, expiração de reserva 10 min, app mobile).

20. **Slide de encerramento** — "Obrigado! Perguntas?", nomes e contatos da equipe, link do repositório GitHub.

**Para cada slide:** escreva um título objetivo (≤ 8 palavras) e 3–5 bullets curtos; reserve áreas visuais para os gráficos do dashboard, os diagramas Mermaid e os screenshots da demonstração.

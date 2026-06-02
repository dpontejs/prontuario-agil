import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import execute_read

st.set_page_config(page_title="Análise CNES", page_icon="📊", layout="wide")
st.title("Análise de Dados Públicos — CNES/DataSUS")
st.markdown("""
Dados do Cadastro Nacional de Estabelecimentos de Saúde — **Rio Grande do Norte** (Abril/2026).
As análises abaixo utilizam dados reais para justificar e validar o sistema Prontuário Ágil.
""")

total_estab = execute_read("SELECT COUNT(*) as total FROM estabelecimento_cnes")[0]["total"]
if total_estab == 0:
    st.warning("Nenhum dado do CNES importado. Execute `python scripts/import_csv.py` primeiro.")
    st.stop()

# ============================================================
# SEÇÃO 1 — PANORAMA GERAL
# ============================================================
st.header("1. Panorama Geral da Saúde no RN")

total_prof = execute_read("SELECT COUNT(*) as total FROM profissional_cnes")[0]["total"]
total_esp = execute_read("SELECT COUNT(DISTINCT cbo) as total FROM profissional_cnes")[0]["total"]
media_prof_estab = execute_read("""
    SELECT AVG(total) as media FROM (
        SELECT COUNT(*) as total FROM profissional_cnes GROUP BY estabelecimento_cnes_id
    ) sub
""")[0]["media"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Estabelecimentos", f"{total_estab:,}".replace(",", "."))
col2.metric("Vínculos Profissionais", f"{total_prof:,}".replace(",", "."))
col3.metric("Especialidades Distintas", total_esp)
col4.metric("Média Prof./Estabelecimento", f"{float(media_prof_estab):.1f}")

st.divider()

# ============================================================
# SEÇÃO 2 — POR QUE UM SISTEMA DE AGENDAMENTO É NECESSÁRIO?
# ============================================================
st.header("2. Por que um sistema de agendamento é necessário?")

st.subheader("2.1 Concentração de profissionais")
st.markdown("""
Poucos estabelecimentos concentram muitos profissionais, gerando **gargalos de agendamento**.
Um sistema como o Prontuário Ágil é essencial para organizar a demanda nesses locais.
""")

top_estab = execute_read("""
    SELECT COALESCE(NULLIF(e.nome_fantasia, ''), CONCAT('CNES ', e.cnes_codigo)) as nome,
           COUNT(*) as total_profissionais
    FROM profissional_cnes p
    JOIN estabelecimento_cnes e ON p.estabelecimento_cnes_id = e.id
    GROUP BY e.id, e.nome_fantasia, e.cnes_codigo
    ORDER BY total_profissionais DESC
    LIMIT 10
""")
df_top = pd.DataFrame(top_estab)
df_top["nome"] = df_top["nome"].str[:40]
fig_top = px.bar(
    df_top, x="total_profissionais", y="nome", orientation="h",
    labels={"nome": "Estabelecimento", "total_profissionais": "Profissionais"},
    title="Top 10 Estabelecimentos com Mais Profissionais"
)
fig_top.update_layout(yaxis=dict(autorange="reversed"), height=400)
st.plotly_chart(fig_top, use_container_width=True)

perc_pequenos = execute_read("""
    SELECT
        ROUND(100.0 * SUM(CASE WHEN total <= 10 THEN 1 ELSE 0 END) / COUNT(*), 1) as percentual
    FROM (SELECT COUNT(*) as total FROM profissional_cnes GROUP BY estabelecimento_cnes_id) sub
""")[0]["percentual"]
st.info(f"**{perc_pequenos}%** dos estabelecimentos têm até 10 profissionais — os poucos grandes concentram a demanda.")

st.subheader("2.2 Carga horária ambulatorial limitada")
st.markdown("""
A carga horária média ambulatorial é **baixa** — cada profissional atende poucas horas por semana.
Isso exige **otimização da agenda** para maximizar o atendimento disponível.
""")

ch_tipo = execute_read("""
    SELECT e.tipo_estabelecimento,
           ROUND(AVG(p.carga_horaria), 1) as media_ch,
           COUNT(*) as total
    FROM profissional_cnes p
    JOIN estabelecimento_cnes e ON p.estabelecimento_cnes_id = e.id
    WHERE p.carga_horaria > 0
    GROUP BY e.tipo_estabelecimento
    HAVING COUNT(*) > 100
    ORDER BY media_ch DESC
    LIMIT 10
""")
df_ch = pd.DataFrame(ch_tipo)
df_ch["media_ch"] = pd.to_numeric(df_ch["media_ch"], errors="coerce").fillna(0).astype(float)
df_ch["tipo_estabelecimento"] = df_ch["tipo_estabelecimento"].str[:35]

fig_ch = px.bar(
    df_ch, x="media_ch", y="tipo_estabelecimento", orientation="h",
    labels={"tipo_estabelecimento": "Tipo", "media_ch": "Carga Horária Média (h)"},
    title="Carga Horária Média por Tipo de Estabelecimento"
)
fig_ch.update_layout(yaxis=dict(autorange="reversed"), height=400)
st.plotly_chart(fig_ch, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 3 — QUAIS ESPECIALIDADES PRIORIZAR?
# ============================================================
st.header("3. Quais especialidades o sistema deve priorizar?")

st.subheader("3.1 Oferta vs Demanda por especialidade")
st.markdown("""
Especialidades com **poucos profissionais** mas **alta carga horária** indicam alta demanda.
São as que mais se beneficiam de um sistema de agendamento eficiente.
""")

scatter_data = execute_read("""
    SELECT cbo as especialidade,
           COUNT(*) as total_profissionais,
           ROUND(AVG(carga_horaria), 1) as media_carga_horaria
    FROM profissional_cnes
    WHERE carga_horaria > 0
    GROUP BY cbo
    HAVING COUNT(*) >= 50
    ORDER BY total_profissionais DESC
    LIMIT 20
""")
df_scatter = pd.DataFrame(scatter_data)
df_scatter["media_carga_horaria"] = pd.to_numeric(df_scatter["media_carga_horaria"], errors="coerce").fillna(0).astype(float)

fig_scatter = px.scatter(
    df_scatter, x="total_profissionais", y="media_carga_horaria",
    hover_name="especialidade",
    size="total_profissionais", size_max=40,
    labels={"total_profissionais": "Total de Profissionais", "media_carga_horaria": "Carga Horária Média (h)"},
    title="Oferta × Demanda: Especialidades no RN (passe o mouse para ver)"
)
fig_scatter.update_layout(height=450, showlegend=False)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("3.2 Especialidades do Prontuário Ágil vs Realidade")
st.markdown("Comparação entre as especialidades cadastradas no sistema e a disponibilidade real no RN:")

esp_sistema = execute_read("SELECT DISTINCT especialidade FROM medico")
if esp_sistema:
    comparativo = []
    for esp in esp_sistema:
        nome = esp["especialidade"]
        termo = nome.upper().split()[0]
        dados = execute_read(
            "SELECT COUNT(*) as total, ROUND(AVG(carga_horaria), 1) as media_ch FROM profissional_cnes WHERE cbo LIKE %s",
            (f"%{termo}%",)
        )[0]
        comparativo.append({
            "Especialidade (Sistema)": nome,
            "Profissionais no RN": dados["total"],
            "Carga Horária Média": f"{float(dados['media_ch'] or 0):.1f}h"
        })
    st.dataframe(pd.DataFrame(comparativo), use_container_width=True, hide_index=True)
else:
    st.info("Cadastre médicos no sistema para ver a comparação.")

st.divider()

# ============================================================
# SEÇÃO 4 — COBERTURA POR MUNICÍPIO
# ============================================================
st.header("4. Cobertura por município")

st.subheader("4.1 Desigualdade na distribuição")

col_top, col_bottom = st.columns(2)

with col_top:
    top_mun = execute_read(
        "SELECT municipio, COUNT(*) as total FROM estabelecimento_cnes GROUP BY municipio ORDER BY total DESC LIMIT 10"
    )
    df_top_mun = pd.DataFrame(top_mun)
    fig_top_mun = px.bar(
        df_top_mun, x="total", y="municipio", orientation="h",
        labels={"municipio": "", "total": "Estabelecimentos"},
        title="Top 10 — Mais estabelecimentos"
    )
    fig_top_mun.update_layout(yaxis=dict(autorange="reversed"), height=350)
    st.plotly_chart(fig_top_mun, use_container_width=True)

with col_bottom:
    bottom_mun = execute_read(
        "SELECT municipio, COUNT(*) as total FROM estabelecimento_cnes GROUP BY municipio ORDER BY total ASC LIMIT 10"
    )
    df_bot_mun = pd.DataFrame(bottom_mun)
    fig_bot_mun = px.bar(
        df_bot_mun, x="total", y="municipio", orientation="h",
        labels={"municipio": "", "total": "Estabelecimentos"},
        title="Bottom 10 — Menos estabelecimentos",
        color_discrete_sequence=["#EF553B"]
    )
    fig_bot_mun.update_layout(yaxis=dict(autorange="reversed"), height=350)
    st.plotly_chart(fig_bot_mun, use_container_width=True)

st.subheader("4.2 Composição dos 5 maiores municípios")
top5_mun = execute_read("""
    SELECT municipio, tipo_estabelecimento, COUNT(*) as total
    FROM estabelecimento_cnes
    GROUP BY municipio, tipo_estabelecimento
    ORDER BY municipio, total DESC
""")
df_cross = pd.DataFrame(top5_mun)
top5_nomes = df_cross.groupby("municipio")["total"].sum().nlargest(5).index.tolist()
df_cross = df_cross[df_cross["municipio"].isin(top5_nomes)]
top5_tipos = df_cross.groupby("tipo_estabelecimento")["total"].sum().nlargest(5).index.tolist()
df_cross = df_cross[df_cross["tipo_estabelecimento"].isin(top5_tipos)]
df_cross["tipo_estabelecimento"] = df_cross["tipo_estabelecimento"].str[:25]

fig_stack = px.bar(
    df_cross, x="municipio", y="total", color="tipo_estabelecimento",
    labels={"municipio": "Município", "total": "Quantidade", "tipo_estabelecimento": "Tipo"},
    title="Tipos de Estabelecimento nos 5 Maiores Municípios"
)
fig_stack.update_layout(height=420, legend=dict(orientation="h", yanchor="bottom", y=-0.4))
st.plotly_chart(fig_stack, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 5 — RESUMO ESTATÍSTICO
# ============================================================
st.header("5. Resumo Estatístico — Funções de Agregação")
st.markdown("Consultas SQL com as funções exigidas, aplicadas aos dados reais:")

resumo = execute_read("""
    SELECT
        MAX(carga_horaria) as maximo,
        MIN(CASE WHEN carga_horaria > 0 THEN carga_horaria END) as minimo_nao_zero,
        ROUND(AVG(carga_horaria), 2) as media,
        SUM(carga_horaria) as soma,
        COUNT(*) as total_vinculos,
        COUNT(DISTINCT cbo) as total_especialidades,
        COUNT(DISTINCT estabelecimento_cnes_id) as total_estabelecimentos_ativos
    FROM profissional_cnes
""")[0]

dados_resumo = {
    "Função SQL": [
        "MAX(carga_horaria)",
        "MIN(carga_horaria) WHERE > 0",
        "AVG(carga_horaria)",
        "SUM(carga_horaria)",
        "COUNT(*)",
        "COUNT(DISTINCT cbo)",
        "COUNT(DISTINCT estabelecimento_cnes_id)"
    ],
    "Descrição": [
        "Maior carga horária registrada",
        "Menor carga horária (excluindo zero)",
        "Média de carga horária ambulatorial",
        "Total de horas ambulatoriais no RN",
        "Total de vínculos profissionais",
        "Total de especialidades distintas",
        "Estabelecimentos com profissionais"
    ],
    "Resultado": [
        f"{resumo['maximo']}h",
        f"{resumo['minimo_nao_zero']}h",
        f"{float(resumo['media']):.2f}h",
        f"{int(resumo['soma']):,}h".replace(",", "."),
        f"{resumo['total_vinculos']:,}".replace(",", "."),
        str(resumo['total_especialidades']),
        str(resumo['total_estabelecimentos_ativos']),
    ]
}
st.dataframe(pd.DataFrame(dados_resumo), use_container_width=True, hide_index=True)

st.subheader("View: vw_estatisticas_especialidade")
st.code("""CREATE VIEW vw_estatisticas_especialidade AS
SELECT cbo AS especialidade,
       COUNT(*) AS total_profissionais,
       AVG(carga_horaria) AS media_carga_horaria,
       MAX(carga_horaria) AS max_carga_horaria,
       MIN(carga_horaria) AS min_carga_horaria,
       SUM(carga_horaria) AS soma_carga_horaria
FROM profissional_cnes
GROUP BY cbo;""", language="sql")

dados_view = execute_read("SELECT * FROM vw_estatisticas_especialidade ORDER BY total_profissionais DESC LIMIT 10")
df_view = pd.DataFrame(dados_view)
if not df_view.empty:
    for col in ["media_carga_horaria", "max_carga_horaria", "min_carga_horaria", "soma_carga_horaria"]:
        df_view[col] = pd.to_numeric(df_view[col], errors="coerce").fillna(0).astype(float)
    df_view["total_profissionais"] = pd.to_numeric(df_view["total_profissionais"], errors="coerce").fillna(0).astype(int)
    st.dataframe(
        df_view.rename(columns={
            "especialidade": "Especialidade",
            "total_profissionais": "Total",
            "media_carga_horaria": "Média (h)",
            "max_carga_horaria": "Máx (h)",
            "min_carga_horaria": "Mín (h)",
            "soma_carga_horaria": "Soma (h)",
        }),
        use_container_width=True, hide_index=True,
    )

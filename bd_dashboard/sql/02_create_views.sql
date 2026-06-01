USE clinica_db;

CREATE OR REPLACE VIEW vw_estatisticas_especialidade AS
SELECT
    cbo AS especialidade,
    COUNT(*) AS total_profissionais,
    AVG(carga_horaria) AS media_carga_horaria,
    MAX(carga_horaria) AS max_carga_horaria,
    MIN(carga_horaria) AS min_carga_horaria,
    SUM(carga_horaria) AS soma_carga_horaria
FROM profissional_cnes
GROUP BY cbo;

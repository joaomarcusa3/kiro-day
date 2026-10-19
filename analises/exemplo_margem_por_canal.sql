-- Exemplo: margem total e margem média (%) por canal de venda.
-- Rode com: docker compose run --rm analise -f analises/exemplo_margem_por_canal.sql
-- Lembre: receita != margem (RN-01 / CS-02). Ranqueie por margem.
SELECT
    canal,
    round(sum(receita_rs))            AS receita_total,
    round(sum(margem_rs))             AS margem_total,
    round(avg(margem_pct), 2)         AS margem_media_pct
FROM plena_comercial_faturamento
GROUP BY canal
ORDER BY margem_total DESC;

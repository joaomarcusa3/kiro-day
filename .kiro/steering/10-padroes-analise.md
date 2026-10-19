---
inclusion: always
---

# Padrões de análise (como entregar)

Estes padrões valem para toda análise feita no workshop. Eles espelham os
`list_coding_standards` e `get_design_guardrails` do MCP `plena-architecture`.

- **CS-01 — Rastreabilidade.** Todo número apresentado deve vir de uma query SQL ou
  script. Nada "de cabeça". Mostre a consulta que gerou o número.
- **CS-02 — Receita ≠ margem.** Nunca conclua rentabilidade só por faturamento.
  Ranqueie por margem (RN-01).
- **CS-03 — % além do kg.** Rendimento de carcaça e perda sempre em % (além do kg),
  para comparar regiões sem enviesar por volume (RN-04).
- **CS-04 — Cite a dimensão.** Todo achado nomeia o recorte: canal, corte, cliente,
  região ou fornecedor.
- **CS-05 — Período fixo.** Apenas abr–set/2025. Não misture outras janelas.
- **CS-06 — Formato fixo.** Exatamente **3 achados + 1 recomendação**.

## Convenções de código

- SQL e Python em `snake_case`; nomes de artefatos com prefixo de intenção
  (`analise_`, `view_`, `campo_`). Use `validate_object_name` do MCP se tiver dúvida.
- Conexão ao banco **sempre** via variável `DATABASE_URL` — sem credencial hardcoded.
- Consultas devem rodar dentro do ambiente Docker do projeto.

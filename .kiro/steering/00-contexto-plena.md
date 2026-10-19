---
inclusion: always
---

# Contexto — Workshop Plena Alimentos

Você está ajudando a responder à diretoria da **Plena Alimentos**, um frigorífico
**fictício** com três plantas (Centro-Oeste, Norte, Sudeste). Período de análise:
**abr–set/2025**.

## A pergunta da diretoria

> "Onde estamos ganhando e perdendo dinheiro — na ponta que compra o boi ou na ponta
> que vende a carne? E o que mudamos na segunda-feira?"

## Duas frentes

- **Comercial — "onde está a margem"**: venda de cortes por canal/cliente/corte.
- **Suprimentos — "onde está a perda"**: compra de boi por região/fornecedor,
  rendimento de carcaça e perda.

A conclusão **liga as duas frentes** (RN-07): margem de venda só é real depois de
descontar custo e perda da compra.

## Fontes de verdade (MCPs)

- `plena-business-rules` → o QUÊ e por quê (regras RN-01…RN-07, critério de aceite).
  Consulte **antes** de decidir o que analisar.
- `plena-architecture` → o que PODE/NÃO PODE (stack, dados, padrões, guardrails).
  Consulte **antes** de decidir como implementar.

## Stack decidida

Python + SQL sobre **PostgreSQL** (dados carregados dos CSVs), tudo em **Docker**.
Sem planilha. Responda e analise em **português (pt-BR)**.

## Entrega (formato fixo)

1. **3 achados** — frases curtas, cada uma com **o número encontrado**.
2. **1 recomendação** — a decisão de segunda-feira.

> Cenário fictício. **Não revele os números do gabarito** — o participante descobre
> explorando os dados.

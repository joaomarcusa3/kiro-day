---
id: case-plena-alimentos
titulo: "Kiro Day — Plena Alimentos: onde ganhamos e perdemos dinheiro?"
dominio: "Análise de dados de negócio (BI / analytics)"
cliente: "Plena Alimentos (frigorífico — cenário fictício)"
tags: [workshop, analytics, amazon-quick, margem, suprimentos, comercial, frigorifico]
---

# Caso de Uso — Workshop Kiro Day · Plena Alimentos

> Cenário **fictício** para workshop. Os números do gabarito **não** são revelados
> aqui de propósito — a sala descobre explorando os dados com o Kiro.

## A empresa

A **Plena Alimentos** é um frigorífico com **três plantas** (Centro-Oeste, Norte e
Sudeste). Compra gado de fazendas de várias regiões e vende cortes de carne por
**quatro canais**: Atacado, Varejo, Food Service e Exportação.

Nos últimos 6 meses (**abr–set/2025**), a diretoria percebeu que o **lucro não cresce
na mesma velocidade que o faturamento**. Antes de contratar consultoria, a diretora
quer uma resposta rápida, feita com os próprios dados, perguntando em português.

## Pergunta da diretoria

> "Onde estamos ganhando e perdendo dinheiro — na ponta que compra o boi ou na ponta
> que vende a carne? E o que mudamos na segunda-feira?"

Restrição: a equipe tem **30 minutos** e o **Kiro** (análise em Python/SQL sobre
PostgreSQL, tudo em Docker). Sem planilha, sem esperar o BI.

## As duas frentes de análise

A pergunta se divide em dois recortes; o time conecta os dois lados no final.

### Frente Comercial — "Onde está a margem?"

Base: **Plena – Comercial / Faturamento** (venda de cortes por canal/cliente).
Entregar resposta para:

- **RN-01** — Qual canal de venda fatura mais e qual realmente dá lucro (receita ≠ margem).
- **RN-02** — Qual tipo de corte puxa a rentabilidade.
- **RN-03** — Quais clientes importam por volume e quais importam por margem (nem sempre são os mesmos).

### Frente Suprimentos — "Onde está a perda?"

Base: **Plena – Suprimentos / Compra de Gado** (compra de boi por região/fornecedor).
Entregar resposta para:

- **RN-04** — Qual região entrega o pior rendimento de carcaça (menos carne por boi comprado).
- **RN-05** — Se existe um fornecedor específico puxando o resultado para baixo.
- **RN-06** — Qual o principal motivo de perda/quebra e se tem relação com região ou manejo.

## Regra de conexão

- **RN-07** — O resultado final liga as duas frentes: a margem comercial (venda) só é
  real depois de descontar o custo e a perda de suprimentos (compra). Receita alta com
  rendimento de carcaça baixo ou fornecedor ruim pode anular o lucro de um canal.

## Objetivo (entregável)

Formato fixo da apresentação:

1. **3 achados** — frases curtas, cada uma com **o número encontrado**.
   (ex.: "O canal X fatura mais, mas o canal Y é o mais rentável.")
2. **1 recomendação** — a decisão de segunda-feira.
   (ex.: "Renegociar com o fornecedor Z e revisar o transporte da região W.")

## Glossário mínimo

- **Rendimento de carcaça** — quanto de carne aproveitável sai por boi comprado
  (kg carcaça ÷ kg vivo). Quanto maior, melhor.
- **Quebra / perda** — peso perdido entre compra e aproveitamento (transporte, manejo,
  condenação sanitária, quebra de resfriamento).
- **Margem** — receita menos custos (do corte e do boi); diferente de faturamento.
- **Canal** — Atacado, Varejo, Food Service, Exportação.

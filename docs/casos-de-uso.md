# Casos de uso — Painel de gestão da Plena

Depois de explorar os dados, a mão na massa é construir um **painel de gestão** para a
diretoria enxergar onde a empresa ganha e perde dinheiro e decidir o que mudar na
segunda-feira. Tudo casando com as regras de negócio que já existem (**RN-01…RN-07**, no
MCP `plena-business-rules`).

Os prompts abaixo estão em **linguagem de negócio** — falam da capacidade e da decisão,
não da tecnologia. O "como" (ferramentas, banco, telas) é descoberto consultando
`plena-business-rules` (o QUÊ e por quê) e `plena-architecture` (o que pode e não pode).
Os hooks `pretask`/`posttask` reforçam essa consulta automaticamente.

---

## Como rodar os casos

- Casos curtos (1, 4, 6) cabem bem no modo **Vibe** (conversa direta).
- Casos maiores (2, 3, 5, 7) rendem mais numa **Spec** (requisitos → design → tarefas),
  com os gates de aprovação.

Prompt de abertura (cole uma vez, antes de qualquer caso):

```
Contexto: workshop Plena Alimentos, periodo abr-set/2025. Antes de propor qualquer
coisa, consulte as regras de negocio (plena-business-rules: RN-01..RN-07 e o criterio
de aceite) e a arquitetura/guardrails (plena-architecture). Quero responder em
portugues e todo numero apresentado precisa ser rastreavel ao dado que o gerou. Nao
revele numeros de gabarito em texto fixo: tudo calculado a partir dos dados.
```

---

## Caso 1 — Onde está a margem? (fácil) · RN-01, RN-02

**Dor da diretoria:** olhamos o faturamento e achamos que o canal que mais vende é o
melhor. Mas faturar muito não é lucrar muito.

**Prompt:**

```
Quero enxergar, lado a lado, quanto cada canal de venda FATURA e quanto cada canal da de
MARGEM, para provar que o canal que mais fatura nao e necessariamente o mais rentavel
(RN-01). Quero tambem ver qual tipo de corte puxa a rentabilidade (RN-02). A leitura tem
que ser imediata: dar para bater o olho e entender onde esta o lucro de verdade.
```

**Pronto quando:** fica visível que o canal campeão de faturamento **não** é o campeão
de margem, e qual corte sustenta a rentabilidade.

---

## Caso 2 — Onde está a perda? (médio) · RN-04, RN-05, RN-06

**Dor da diretoria:** sabemos que perdemos carne entre a compra do boi e o
aproveitamento, mas não sabemos **onde** nem **de quem**.

**Prompt:**

```
Quero descobrir onde a Plena perde rendimento e dinheiro na compra do gado. Preciso ver
qual regiao entrega o pior rendimento de carcaca (RN-04), se existe um fornecedor
especifico puxando o resultado para baixo (RN-05) e qual e o principal motivo de perda
(RN-06). Compare as regioes de forma justa, sem que uma pareca pior so por comprar mais
volume. Quero poder agir: identificar com quem renegociar e o que corrigir no manejo ou
transporte.
```

**Pronto quando:** dá para apontar a pior região por rendimento, o fornecedor
problemático e o motivo de perda dominante — com número, não "no achismo".

---

## Caso 3 — Qual é o lucro real? (difícil) · RN-07 + gestão

**Dor da diretoria:** a margem de venda parece boa, mas ela não desconta o que perdemos
na compra. O lucro que comemoramos pode ser ilusório.

**Prompt:**

```
Quero o lucro REAL por planta, conectando as duas frentes (RN-07): a margem da venda
menos o impacto do custo e da perda na compra do gado. Alem disso, quero um painel de
alertas de gestao para agir cedo: avisar quando um canal fica com margem abaixo de um
limite, quando uma regiao fica abaixo da meta de rendimento e quando um fornecedor passa
de um teto de perda. Por fim, quero poder gerar a entrega no formato da diretoria: 3
achados (cada um com o numero) + 1 recomendacao, ligando a ponta que vende a ponta que
compra.
```

**Pronto quando:** a diretoria vê o lucro real por planta (não só a margem bruta),
recebe alertas acionáveis e consegue gerar os **3 achados + 1 recomendação**.

---

## Caso 4 — Quem são meus clientes de verdade? (fácil) · RN-03

**Dor da diretoria:** tratamos como "melhores clientes" quem compra mais volume, mas
alguns deles dão pouca margem — e clientes menores podem ser os mais rentáveis.

**Prompt:**

```
Quero separar os clientes que importam por VOLUME dos que importam por MARGEM (RN-03).
Preciso ver, de um lado, quem mais compra em quilos/faturamento e, de outro, quem mais
contribui para a margem — e destacar quando NAO sao os mesmos. A ideia e saber a quem
dar atencao comercial sem confundir tamanho com rentabilidade.
```

**Pronto quando:** fica claro que o ranking "por volume" e o ranking "por margem" têm
nomes diferentes no topo, e dá para ver quais clientes merecem prioridade.

---

## Caso 5 — Comparar as três plantas (médio) · RN-01, RN-04, RN-07

**Dor da diretoria:** temos três plantas (Centro-Oeste, Norte, Sudeste) e não sabemos
qual é a mais saudável de ponta a ponta.

**Prompt:**

```
Quero comparar as tres plantas lado a lado, de ponta a ponta: de um lado a margem das
vendas (RN-01), do outro o rendimento de carcaca e a perda na compra (RN-04), e no final
o lucro real de cada planta (RN-07). Quero um ranking das plantas que considere a
operacao inteira, nao so a venda, para saber onde esta o melhor e o pior desempenho e
por que.
```

**Pronto quando:** existe um ranking das plantas por lucro real, com o porquê (margem boa
mas perda alta, ou o contrário) visível para cada uma.

---

## Caso 6 — A operação está melhorando ou piorando? (médio) · todas as frentes

**Dor da diretoria:** olhamos só o acumulado e não enxergamos a tendência mês a mês
dentro da janela abr–set/2025.

**Prompt:**

```
Quero ver a evolucao mes a mes (abr a set/2025) das metricas que importam: faturamento,
margem, rendimento de carcaca medio e perda. Quero perceber se a margem esta encolhendo
enquanto o faturamento cresce, e se o rendimento ou a perda estao piorando ao longo do
periodo. Nada fora da janela abr-set/2025.
```

**Pronto quando:** dá para ler a tendência (melhorando/piorando) de cada métrica no
período, e enxergar o descolamento entre faturamento e margem no tempo.

---

## Caso 7 — Simular a decisão de segunda-feira (difícil) · RN-05, RN-06, RN-07

**Dor da diretoria:** queremos testar o impacto de uma decisão antes de tomá-la: trocar
um fornecedor ruim, corrigir um motivo de perda, focar num canal mais rentável.

**Prompt:**

```
Quero simular o efeito de decisoes de gestao sobre o lucro real (RN-07). Por exemplo: se
eu trocar o fornecedor que puxa o resultado para baixo (RN-05) por um de rendimento
medio, quanto a Plena recupera? Se eu reduzir o principal motivo de perda (RN-06) em uma
fracao, qual o ganho? Quero poder ajustar essas premissas e ver o lucro real recalculado,
para embasar a recomendacao da entrega.
```

**Pronto quando:** dá para mexer numa premissa (fornecedor, perda, foco de canal) e ver
o lucro real recalculado, sustentando a recomendação com número.

---

## Lembrete das regras (valem para todos os casos)

- **RN-01** — Receita ≠ margem: rentabilidade se mede por margem, não por faturamento.
- **RN-02** — Identificar o corte que puxa a rentabilidade.
- **RN-03** — Separar cliente que importa por volume de cliente que importa por margem.
- **RN-04** — Comparar rendimento de carcaça de forma justa entre regiões (em %).
- **RN-05** — Isolar o fornecedor que puxa o resultado para baixo.
- **RN-06** — Achar o principal motivo de perda e ligá-lo a região ou manejo.
- **RN-07** — A margem de venda só é real depois de descontar custo e perda da compra.

> O critério de aceite completo (Given/When/Then) está em `plena-business-rules`
> (`get_acceptance_criteria`). A entrega é sempre **3 achados + 1 recomendação**, em
> português, com os números descobertos a partir dos dados.

# Kiro Day · Plena Alimentos — onde ganhamos e perdemos dinheiro?

Workshop prático de análise de dados de negócio com o **Kiro**. Você clona este
projeto, sobe tudo no **Docker** e usa o Kiro (com MCPs, steerings e hooks) para
responder à diretoria de um frigorífico fictício — em **português**, no formato
**3 achados + 1 recomendação**.

> Cenário **fictício**. Os números do "gabarito" não são revelados — você descobre
> explorando os dados.

---

## O caso

A **Plena Alimentos** é um frigorífico com três plantas (Centro-Oeste, Norte,
Sudeste). Nos últimos 6 meses (**abr–set/2025**) o lucro não cresce na velocidade do
faturamento. A pergunta da diretoria:

> "Onde estamos ganhando e perdendo dinheiro — na ponta que compra o boi ou na ponta
> que vende a carne? E o que mudamos na segunda-feira?"

Duas frentes:

| Frente | Base | Perguntas |
|---|---|---|
| **Comercial — "onde está a margem"** | `plena_comercial_faturamento` | Qual canal fatura mais e qual dá lucro? Qual corte puxa a rentabilidade? Quais clientes importam por volume x por margem? |
| **Suprimentos — "onde está a perda"** | `plena_suprimentos_compra_gado` | Qual região tem pior rendimento de carcaça? Há um fornecedor puxando para baixo? Qual o principal motivo de perda? |

**Entrega:** 3 achados (cada um com o número) + 1 recomendação. A conclusão liga as
duas frentes — margem de venda só é real depois de descontar custo e perda da compra.

---

## Pré-requisitos

- **Docker Desktop** rodando (`docker --version` e `docker compose version`).
- **Kiro** (este projeto já traz a config de MCP, steerings e hooks).
- Não precisa de Python, `uv` ou Postgres instalados na máquina — tudo roda em Docker.

---

## Passo a passo

### 1. Clonar e abrir

```bash
git clone <url-do-repo> plena-workshop
cd plena-workshop
```

Abra a pasta no Kiro.

### 2. Subir os dados no Docker

(Opcional) copie o arquivo de ambiente — tem defaults, então só mude se precisar
(ex.: trocar a porta do Postgres no host):

```bash
cp .env.example .env
```

Um único comando constrói a imagem, sobe o Postgres e carrega os dois datasets:

```bash
docker compose up --build seed
```

Você deve ver:

```
plena_comercial_faturamento: 2802 linhas carregadas
plena_suprimentos_compra_gado: 1929 linhas carregadas
Carga concluída.
```

O Postgres fica de pé em background (porta **5544** no host → 5432 no container).
Pare tudo ao final com `docker compose down` (os dados persistem no volume
`plena-pgdata`; para apagar também os dados use `docker compose down -v`).

### 3. Conectar os MCPs do Kiro

Os dois MCP servers (regras de negócio e arquitetura) **rodam em Docker**. Copie a
config de exemplo para a pasta de settings do Kiro:

```bash
mkdir -p .kiro/settings
cp mcp.example.json .kiro/settings/mcp.json
```

No Kiro, abra a visão de **MCP Servers** e confirme que aparecem conectados:

- `plena-business-rules` → o QUÊ e por quê (regras **RN-01…RN-07**, critério de aceite).
- `plena-architecture` → o que PODE/NÃO PODE (stack, dados, padrões, guardrails).

> A config usa `docker compose run`, então funciona em qualquer máquina sem caminhos
> fixos. A imagem precisa ter sido construída no passo 2.

### 4. Explorar os dados

Rode consultas contra o Postgres pelo runner em Docker (sem instalar nada):

```bash
# SQL direto
docker compose run --rm analise "SELECT canal, round(sum(receita_rs)) AS receita, round(sum(margem_rs)) AS margem FROM plena_comercial_faturamento GROUP BY canal ORDER BY margem DESC"

# ou a partir de um arquivo .sql em analises/
docker compose run --rm analise -f analises/exemplo_margem_por_canal.sql
```

Há um exemplo pronto em `analises/exemplo_margem_por_canal.sql`. Crie os seus `.sql`
nessa pasta — ela é montada dentro do container.

### 5. Analisar com o Kiro

Converse com o Kiro em português. Ele já tem contexto (steerings) e as fontes de
verdade (MCPs). Exemplos de pedido:

> "Consulte as regras da Plena e me ajude a descobrir qual canal é o mais rentável —
> lembre que receita ≠ margem."

> "Qual região tem o pior rendimento de carcaça? Tem algum fornecedor puxando o
> resultado para baixo? Mostre a query."

O Kiro consulta os MCPs, propõe consultas SQL, roda no Docker e organiza os achados.

### 6. Montar a entrega

Peça ao Kiro para fechar no formato fixo: **3 achados** (cada um com o número e a
dimensão: canal/corte/cliente/região/fornecedor) **+ 1 recomendação** (a decisão de
segunda-feira), conectando as duas frentes.

> **Quer ir além?** Em `docs/casos-de-uso.md` há 3 casos de uso (com prompts prontos)
> para construir um dashboard de gestão com o Kiro, casando com as regras RN-01…RN-07.

---

## Onde entram steerings e hooks

### Steerings (`.kiro/steering/`) — contexto sempre presente

Instruções que o Kiro carrega automaticamente em toda conversa deste workspace:

| Arquivo | Para quê |
|---|---|
| `00-contexto-plena.md` | O caso, as duas frentes, as fontes de verdade (MCPs) e o formato da entrega. |
| `10-padroes-analise.md` | Os padrões (CS-01…CS-06): rastreabilidade do número, receita ≠ margem, % de rendimento, período fixo, formato. |

> Edite-os para mudar o comportamento do Kiro no workshop. É aqui que você ensina as
> "regras da casa" sem repetir em cada prompt.

### Hooks (`.kiro/hooks/`) — automação por evento

Disparam sozinhos em eventos do Kiro:

| Hook | Dispara em | O que faz |
|---|---|---|
| `pretask-consultar-regras` | antes de cada tarefa de spec (`PreTaskExec`) | lembra o Kiro de consultar `plena-business-rules` e `plena-architecture` antes de implementar. |
| `posttask-checar-entrega` | depois de cada tarefa (`PostTaskExec`) | valida os guardrails (número rastreável, margem ≠ receita, % de rendimento, período, formato 3+1). |
| `lint-sql-on-save` | ao salvar um `.sql` (`PostFileSave`) | lembra como executar a query no Docker. |

> Veja/edite na seção **Agent Hooks** do Kiro, ou direto nos JSONs em `.kiro/hooks/`.

---

## Estrutura do projeto

```
.
├── docker-compose.yml           # Postgres + seed + análise + 2 MCP servers
├── Dockerfile                   # imagem Python (MCPs + gerador + runner de SQL)
├── requirements.txt
├── .env.example                 # variáveis de ambiente (copie para .env)
├── mcp.example.json             # config MCP para copiar em .kiro/settings/mcp.json
├── analises/                    # seus .sql (montado no container de análise)
├── docs/                        # casos-de-uso.md e material de apoio
└── .kiro/
    ├── steering/                # contexto sempre presente
    ├── hooks/                   # automação por evento
    └── mcp-servers/
        ├── business-rules/      # MCP: regras de negócio (RN-01…RN-07)
        ├── architecture/        # MCP: stack, dados, padrões, guardrails
        └── plena-datasets/      # gerador dos CSVs, carga no Postgres, runner de SQL
```

---

## Comandos úteis

| Objetivo | Comando |
|---|---|
| Subir dados (build + Postgres + carga) | `docker compose up --build seed` |
| Recarregar os dados do zero | `docker compose run --rm seed` |
| Rodar uma query | `docker compose run --rm analise "SELECT ..."` |
| Rodar um arquivo SQL | `docker compose run --rm analise -f analises/arquivo.sql` |
| Shell interativo no container | `docker compose run --rm --entrypoint bash analise` |
| Parar tudo | `docker compose down` |
| Parar e apagar os dados | `docker compose down -v` |

---

## Solução de problemas

| Sintoma | Ação |
|---|---|
| MCP não conecta no Kiro | Garanta que a imagem foi construída (`docker compose up --build seed`) e que `.kiro/settings/mcp.json` existe; reconecte no Kiro. |
| `port is already allocated` | Outro Postgres usa a 5544 no host. Ajuste a porta em `docker-compose.yml` (lado esquerdo do `5544:5432`). |
| `DATABASE_URL não definida` | Use os comandos via `docker compose` — a variável já vem setada nos serviços. |
| Dados parecem antigos | `docker compose down -v` e suba de novo para recriar o volume. |

---

## Dicionário de dados

### `plena_comercial_faturamento` (frente Comercial)

`venda_id, data, mes, planta, canal, cliente, corte, quantidade_kg, preco_kg,`
`receita_rs, margem_rs, margem_pct`

### `plena_suprimentos_compra_gado` (frente Suprimentos)

`compra_id, data, mes, planta, regiao_origem, fornecedor, cabecas, peso_vivo_kg,`
`peso_carcaca_kg, rendimento_carcaca_pct, perda_kg, motivo_perda, preco_arroba_rs,`
`custo_total_rs`

> **Rendimento de carcaça** = kg carcaça ÷ kg vivo (maior é melhor). **Perda/quebra** =
> peso perdido entre compra e aproveitamento. **Margem** = receita menos custos
> (diferente de faturamento).

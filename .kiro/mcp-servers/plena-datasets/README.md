# Datasets — Kiro Day · Plena Alimentos

Dados **sintéticos e fictícios** para o workshop. Dois CSVs que são carregados no
**PostgreSQL** (via Docker) e analisados com o **Kiro** para responder à pergunta da
diretoria (onde a Plena ganha e perde dinheiro, abr–set/2025).

## Arquivos deste diretório

| Arquivo | Papel |
|---|---|
| `generate_datasets.py` | Gera os dois CSVs em `data/` (semente fixa, reprodutível). |
| `load_to_postgres.py` | Carrega os CSVs no Postgres (DROP + CREATE + COPY). Conexão via `DATABASE_URL`. |
| `query.py` | Runner de SQL via `psycopg` (sem `psql`). Usado pelo serviço `analise` do compose. |
| `data/*.csv` | Saída do gerador (recriada no build; ignorada no git). |

> No workshop você **não** roda esses scripts à mão — o `docker compose` cuida de
> tudo. Veja o passo a passo no `README.md` da raiz. Os comandos abaixo são só
> referência de quem quiser rodar isolado.

## Fluxo no Docker (referência)

```bash
# da raiz do projeto
docker compose up --build seed     # gera CSVs (no build), sobe Postgres e carrega as tabelas
```

Tabelas criadas no Postgres:

| Tabela | Frente | Grão |
|---|---|---|
| `plena_comercial_faturamento` | Comercial — "onde está a margem" | 1 linha por venda |
| `plena_suprimentos_compra_gado` | Suprimentos — "onde está a perda" | 1 linha por compra |

Consultar:

```bash
docker compose run --rm analise "SELECT canal, round(sum(margem_rs)) FROM plena_comercial_faturamento GROUP BY 1 ORDER BY 2 DESC"
docker compose run --rm analise -f analises/exemplo_margem_por_canal.sql
```

## Dicionário de dados

### `plena_comercial_faturamento` (Comercial / Faturamento)

| Campo | Descrição |
|---|---|
| `venda_id` | Identificador da venda |
| `data`, `mes` | Data e competência (AAAA-MM) |
| `planta` | Centro-Oeste, Norte ou Sudeste |
| `canal` | Atacado, Varejo, Food Service, Exportação |
| `cliente` | Cliente do canal |
| `corte` | Tipo de corte de carne |
| `quantidade_kg` | Quantidade vendida (kg) |
| `preco_kg` | Preço por kg (R$) |
| `receita_rs` | Receita da venda (R$) |
| `margem_rs` | Margem em reais (R$) |
| `margem_pct` | Margem percentual (%) |

### `plena_suprimentos_compra_gado` (Suprimentos / Compra de Gado)

| Campo | Descrição |
|---|---|
| `compra_id` | Identificador da compra |
| `data`, `mes` | Data e competência (AAAA-MM) |
| `planta` | Planta que recebeu o gado |
| `regiao_origem` | Região de origem do boi |
| `fornecedor` | Fazenda/pecuária fornecedora |
| `cabecas` | Nº de cabeças |
| `peso_vivo_kg` | Peso vivo total (kg) |
| `peso_carcaca_kg` | Peso de carcaça aproveitável (kg) |
| `rendimento_carcaca_pct` | Rendimento de carcaça (%) = carcaça ÷ vivo |
| `perda_kg` | Perda/quebra (kg) |
| `motivo_perda` | Principal motivo da perda |
| `preco_arroba_rs` | Preço da arroba (R$) |
| `custo_total_rs` | Custo total da compra (R$) |

## Como usar com o Kiro

1. Suba os dados (`docker compose up --build seed`).
2. Conecte os MCPs (`cp mcp.example.json .kiro/settings/mcp.json`) e reconecte no Kiro.
3. Pergunte em **português** ao Kiro (ex.: "qual canal tem a maior margem total?",
   "qual região tem o menor rendimento de carcaça médio?"). O Kiro consulta os MCPs,
   propõe a query SQL e roda no Docker.
4. Monte a entrega: **3 achados** (cada um com o número) **+ 1 recomendação**.

> Os números do "gabarito" estão embutidos nos dados de propósito — descubra-os
> explorando, não há planilha de respostas. Semente fixa (`random.seed(2025)`) para
> reprodutibilidade entre execuções.

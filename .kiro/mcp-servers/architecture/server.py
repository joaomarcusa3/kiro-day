"""
MCP · Architecture
==================
Servidor MCP local que SIMULA o landscape de ANÁLISE DE DADOS do workshop
"Plena Alimentos". Fornece ao agente as RESTRIÇÕES e DECISÕES do ambiente de
analytics: fontes de dados, stack técnica, ambientes, padrões e guardrails para
responder à diretoria com os próprios dados.

É complementar ao outro MCP:
  - business-rules → o QUÊ e por quê (perguntas da diretoria, critério de aceite)
  - architecture   → o que PODE e o que NÃO PODE ser usado (stack, dados, padrões)

⚠️  DADOS FICTÍCIOS/REPRESENTATIVOS. Cenário de workshop, não produtivo.

Executado em container (Docker). Localmente: python server.py   (transporte stdio)
"""

from __future__ import annotations

import re

from fastmcp import FastMCP

mcp = FastMCP("architecture")

# --------------------------------------------------------------------------- #
# Landscape (dados representativos) — ambiente de análise da Plena Alimentos
# --------------------------------------------------------------------------- #
SYSTEMS = {
    "ANALYTICS": {
        "id": "ANALYTICS",
        "nome": "Análise em Python (pandas + SQL sobre Postgres)",
        "papel": "Exploração dos dados e respostas à diretoria, em português",
        "modulos": ["Ingestão (CSV → Postgres)", "Consultas SQL", "Análise em Python"],
        "deployment": "Containers (Docker) — Postgres + scripts Python",
    },
    "COMERCIAL": {
        "id": "COMERCIAL",
        "nome": "Base Comercial / Faturamento",
        "papel": "Venda de cortes por planta/canal/cliente (frente 'onde está a margem')",
        "modulos": ["Faturamento", "CRM de canais"],
        "deployment": "Tabela plena_comercial_faturamento no Postgres (carga via CSV)",
    },
    "SUPRIMENTOS": {
        "id": "SUPRIMENTOS",
        "nome": "Base Suprimentos / Compra de Gado",
        "papel": "Compra de boi por região/fornecedor, rendimento e perda (frente 'onde está a perda')",
        "modulos": ["Compras", "Abate/Rendimento"],
        "deployment": "Tabela plena_suprimentos_compra_gado no Postgres (carga via CSV)",
    },
}

TECH_STACK = [
    {"camada": "Linguagem", "tecnologia": "Python 3.14", "uso": "Ingestão, consultas e análise dos dados"},
    {"camada": "Banco de dados", "tecnologia": "PostgreSQL 16", "uso": "Armazena os dois datasets e serve as consultas SQL"},
    {"camada": "Acesso ao banco", "tecnologia": "psycopg 3", "uso": "Conexão e COPY dos CSVs para o Postgres"},
    {"camada": "Fontes de dados", "tecnologia": "Datasets CSV (Comercial, Suprimentos)", "uso": "Carregados no Postgres como tabelas"},
    {"camada": "Modelagem", "tecnologia": "SQL / campos derivados em Python", "uso": "Margem, rendimento de carcaça, perda — direto nas consultas"},
    {"camada": "Empacotamento", "tecnologia": "Docker + docker-compose", "uso": "Sobe Postgres e roda a carga/análise em containers"},
    {"camada": "Período de análise", "tecnologia": "abr–set/2025", "uso": "Janela fixa do case; não usar dados fora dela"},
    {"camada": "Idioma", "tecnologia": "Português (pt-BR)", "uso": "Perguntas e respostas da diretoria em português"},
    {"camada": "Entrega", "tecnologia": "3 achados + 1 recomendação", "uso": "Formato fixo da apresentação final"},
]

DATABASE = {
    "sgbd": "PostgreSQL 16",
    "observacao": "Os dois CSVs da Plena são carregados como tabelas no Postgres (script load_to_postgres.py).",
    "conexao": "postgresql://plena:plena@postgres:5432/plena (via variável DATABASE_URL)",
    "tabelas_relevantes": [
        {"tabela": "plena_comercial_faturamento", "descricao": "Venda de cortes: planta, canal, cliente, corte, receita, margem"},
        {"tabela": "plena_suprimentos_compra_gado", "descricao": "Compra de boi: região, fornecedor, rendimento de carcaça, perda, custo"},
    ],
    "acesso_recomendado": "Consultar via SQL (ou pandas lendo do Postgres); derivar métricas na própria query",
    "campos_calculados_sugeridos": [
        "margem_pct = margem_rs / receita_rs",
        "rendimento_carcaca_pct = peso_carcaca_kg / peso_vivo_kg",
        "perda_pct = perda_kg / peso_vivo_kg",
    ],
}

INTERFACES = {
    "LOAD": {
        "id": "LOAD",
        "nome": "Carga de CSV no Postgres",
        "tipo": "Ingestão de dados",
        "direcao": "CSV → PostgreSQL",
        "criticidade": "Alta",
        "observacao": "Carregar os dois CSVs como tabelas (COPY) antes de analisar.",
    },
    "SQL": {
        "id": "SQL",
        "nome": "Consulta SQL / análise em Python",
        "tipo": "Consulta",
        "direcao": "Python → PostgreSQL",
        "criticidade": "Alta",
        "observacao": "Rodar as agregações em SQL; validar o número antes de concluir.",
    },
    "REPORT": {
        "id": "REPORT",
        "nome": "Saída da análise (achados)",
        "tipo": "Apresentação",
        "direcao": "Análise → diretoria",
        "criticidade": "Média",
        "observacao": "Suporte aos 3 achados; cada número rastreável à query que o gerou.",
    },
}

ENVIRONMENTS = {
    "LOCAL": {"sid": "LOCAL", "nome": "Ambiente local (docker-compose)", "uso": "Postgres + análise em containers", "transporta_para": None},
}
TRANSPORT_ROUTE = "CSV → Postgres (COPY) → Consulta SQL/Python → Apresentação (3 achados + 1 recomendação)"

CODING_STANDARDS = [
    {"id": "CS-01", "regra": "Todo número apresentado deve ser rastreável a uma query SQL/script (nada 'de cabeça')."},
    {"id": "CS-02", "regra": "Separar receita de margem — nunca concluir rentabilidade só por faturamento (RN-01)."},
    {"id": "CS-03", "regra": "Rendimento de carcaça e perda sempre em % além do kg, para comparar entre regiões (RN-04)."},
    {"id": "CS-04", "regra": "Citar a dimensão do achado: canal, corte, cliente, região ou fornecedor."},
    {"id": "CS-05", "regra": "Respeitar o período abr–set/2025; não misturar outras janelas."},
    {"id": "CS-06", "regra": "Entrega no formato fixo: exatamente 3 achados + 1 recomendação."},
]

# Restrições / o que NÃO pode ser feito
DESIGN_CONSTRAINTS = [
    {"tipo": "Escopo", "regra": "Não revelar os números do gabarito antes da sala descobrir."},
    {"tipo": "Ferramenta", "regra": "Análise em Python/SQL sobre Postgres — sem planilha e sem esperar o time de BI."},
    {"tipo": "Rigor", "regra": "Receita ≠ margem: ranquear rentabilidade por margem, não por faturamento (RN-01)."},
    {"tipo": "Consistência", "regra": "Comparar rendimento de carcaça em % para não enviesar por volume (RN-04)."},
    {"tipo": "Conexão", "regra": "Ligar as duas frentes: margem comercial só é real após custo/perda de suprimentos (RN-07)."},
    {"tipo": "Janela", "regra": "Período fixo abr–set/2025; sem forecast ou dados fora da janela."},
    {"tipo": "Simplicidade", "regra": "Responder à pergunta com os dados dados. NÃO propor troca de ERP, data lake ou ML — fora de escopo no workshop."},
]

# Decisões de arquitetura já tomadas — o agente deve assumir como dadas
ARCHITECTURE_DECISIONS = [
    {
        "id": "AD-01",
        "titulo": "Análise feita em Python sobre Postgres",
        "decisao": "A exploração e as respostas à diretoria são feitas em Python (SQL/pandas) com os dados no PostgreSQL.",
        "motivo": "Resposta rápida com os próprios dados, reprodutível e versionável, sem depender do time de BI.",
        "implicacoes": "Os CSVs são carregados como tabelas no Postgres; métricas derivadas nas queries; sem planilha.",
    },
    {
        "id": "AD-02",
        "titulo": "Duas frentes conectadas",
        "decisao": "A análise tem duas frentes (Comercial/margem e Suprimentos/perda) que são conectadas na conclusão.",
        "motivo": "A pergunta da diretoria abrange a ponta que vende e a ponta que compra.",
        "implicacoes": "Cada frente usa sua tabela; o achado final liga margem de venda a custo/perda de compra (RN-07).",
    },
    {
        "id": "AD-03",
        "titulo": "Entrega em formato fixo",
        "decisao": "A saída é sempre 3 achados (cada um com um número) + 1 recomendação (a decisão de segunda-feira).",
        "motivo": "Foco em decisão de negócio, não em relatório extenso.",
        "implicacoes": "Achados curtos, numéricos e rastreáveis; uma única recomendação acionável.",
    },
    {
        "id": "AD-04",
        "titulo": "Ambiente conteinerizado (Docker)",
        "decisao": "O Postgres e os scripts de carga/análise rodam via docker-compose, preparando o deploy.",
        "motivo": "Ambiente reprodutível e portável entre máquinas do workshop.",
        "implicacoes": "Conexão via DATABASE_URL; sem hardcode de credenciais no código; volume persiste os dados do Postgres.",
    },
]


def _norm(s: str) -> str:
    return (s or "").strip().upper()


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
@mcp.tool()
def get_landscape() -> dict:
    """Visão geral do ambiente de análise (stack, fontes de dados e fluxo)."""
    return {
        "sistemas": list(SYSTEMS.values()),
        "ambientes": list(ENVIRONMENTS.values()),
        "fluxo": TRANSPORT_ROUTE,
        "resumo": "Análise em Python/SQL sobre Postgres com dois datasets (Comercial e Suprimentos) da Plena Alimentos; pt-BR.",
    }


@mcp.tool()
def list_systems() -> list[dict]:
    """Lista os componentes do ambiente (camada de análise e as duas bases de dados)."""
    return list(SYSTEMS.values())


@mcp.tool()
def get_system(system_id: str) -> dict:
    """Detalha um componente do ambiente.

    Args:
        system_id: identificador (ANALYTICS, COMERCIAL, SUPRIMENTOS).
    """
    s = SYSTEMS.get(_norm(system_id))
    return s or {"erro": f"Sistema '{system_id}' não encontrado.", "disponiveis": list(SYSTEMS)}


@mcp.tool()
def list_tech_stack() -> list[dict]:
    """Lista o stack por camada (linguagem, banco, acesso, fontes, modelagem, empacotamento, período, idioma, entrega)."""
    return TECH_STACK


@mcp.tool()
def get_database() -> dict:
    """Detalha a base de dados (PostgreSQL), tabelas, conexão e campos calculados sugeridos."""
    return DATABASE


@mcp.tool()
def list_interfaces() -> list[dict]:
    """Lista as interfaces do ambiente (carga de CSV, consulta SQL, saída da análise)."""
    return list(INTERFACES.values())


@mcp.tool()
def get_interface(interface_id: str) -> dict:
    """Detalha uma interface.

    Args:
        interface_id: identificador (LOAD, SQL, REPORT).
    """
    i = INTERFACES.get(_norm(interface_id))
    return i or {"erro": f"Interface '{interface_id}' não encontrada.", "disponiveis": list(INTERFACES)}


@mcp.tool()
def get_environments() -> dict:
    """Retorna o ambiente do workshop e o fluxo da análise."""
    return {"ambientes": ENVIRONMENTS, "fluxo": TRANSPORT_ROUTE}


@mcp.tool()
def list_coding_standards() -> list[dict]:
    """Lista os padrões de análise (rastreabilidade do número, receita≠margem, % de rendimento, dimensão, período, formato)."""
    return CODING_STANDARDS


@mcp.tool()
def list_design_constraints() -> list[dict]:
    """Lista as restrições — o que NÃO pode ser feito (revelar gabarito, usar planilha, confundir receita com margem, etc.).

    Use na Construction (Gate 2) para garantir que a análise respeita o que o negócio definiu.
    """
    return DESIGN_CONSTRAINTS


@mcp.tool()
def get_design_guardrails() -> dict:
    """Consolida os guardrails que a análise/entrega DEVE satisfazer (checklist para o Gate 2)."""
    return {
        "guardrails": [
            "Ranquear rentabilidade por MARGEM, não por faturamento (RN-01, CS-02).",
            "Comparar regiões por rendimento de carcaça em % (RN-04, CS-03).",
            "Isolar o fornecedor que puxa o resultado para baixo (RN-05) com número.",
            "Identificar o principal motivo de perda e relacioná-lo a região/manejo (RN-06).",
            "Conectar as duas frentes na conclusão (RN-07).",
            "Todo número rastreável a uma query SQL/script (CS-01); período abr–set/2025 (CS-05).",
            "Entregar exatamente 3 achados + 1 recomendação (CS-06).",
        ],
        "referencia": "Combine com get_acceptance_criteria (business-rules) para o formato da entrega.",
    }


@mcp.tool()
def validate_object_name(name: str) -> dict:
    """Valida o nome de um artefato de análise (tabela/view/script/campo) contra convenções simples.

    Args:
        name: nome do artefato (ex.: analise_margem_por_canal).
    """
    n = (name or "").strip()
    problemas: list[str] = []
    if not n:
        return {"nome": name, "valido": False, "problemas": ["Nome vazio."]}
    if not re.match(r"^[a-z0-9_]+$", n):
        problemas.append("Use minúsculas, números e '_' (snake_case) para tabelas/campos/scripts.")
    if len(n) > 60:
        problemas.append("Nome muito longo (> 60 caracteres).")
    sugestao = None
    if re.match(r"^[a-z0-9_]+$", n) and not n.startswith(("analise_", "tabela_", "view_", "campo_", "plena_")):
        sugestao = f"Considere um prefixo de intenção, ex.: analise_{n} ou view_{n}."
    return {"nome": name, "valido": not problemas, "problemas": problemas, "sugestao": sugestao}


@mcp.tool()
def list_architecture_decisions() -> list[dict]:
    """Lista as decisões já tomadas (ADRs) que o agente deve assumir como dadas:
    análise em Python sobre Postgres, duas frentes conectadas, entrega em formato fixo e ambiente conteinerizado."""
    return ARCHITECTURE_DECISIONS


@mcp.tool()
def get_analysis_stack() -> dict:
    """Retorna a stack decidida para a análise da Plena (Python + SQL sobre PostgreSQL).

    Use quando o alvo for conduzir a análise: a stack já está decidida (AD-01).
    """
    return {
        "linguagem": "Python 3.14",
        "banco": "PostgreSQL 16 (psycopg 3)",
        "idioma": "Português (pt-BR)",
        "fontes": ["plena_comercial_faturamento", "plena_suprimentos_compra_gado"],
        "modelagem": "Métricas derivadas em SQL/pandas (margem, rendimento, perda) — sem ETL externo",
        "periodo": "abr–set/2025",
        "entrega": "3 achados (com número) + 1 recomendação",
        "governanca": "Não revelar o gabarito; a sala descobre (AD-03)",
        "principio_simplicidade": (
            "Responder à pergunta com os dados fornecidos. NÃO propor troca de ERP, "
            "data lake, pipeline de ETL ou ML — fora de escopo no workshop."
        ),
        "referencia": "Decisões AD-01, AD-02 e AD-03",
    }


@mcp.tool()
def get_deploy_config() -> dict:
    """Retorna a configuração de deploy do ambiente (Docker + Postgres).

    O Postgres e os scripts de carga/análise rodam via docker-compose. A conexão
    ao banco é parametrizada por DATABASE_URL — sem hardcode de credenciais.
    """
    return {
        "orquestracao": "docker-compose (serviços: postgres + seed)",
        "banco": "PostgreSQL 16 (imagem postgres:16-alpine), volume persistente plena-pgdata",
        "conexao": "DATABASE_URL=postgresql://plena:plena@postgres:5432/plena",
        "carga": "python mcp-servers/plena-datasets/load_to_postgres.py (DROP + CREATE + COPY)",
        "credenciais": "Parametrizadas por variáveis de ambiente — sem hardcode no código.",
        "verificacao": "docker compose up; conferir contagem de linhas impressa pelo serviço de seed.",
        "referencia": "Decisão AD-04",
    }


if __name__ == "__main__":
    mcp.run()

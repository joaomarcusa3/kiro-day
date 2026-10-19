"""
MCP · Business Rules
====================
Servidor MCP local que expõe as regras de negócio do domínio como contexto
consultável pelo Kiro. Neste workshop o caso de exemplo é o "Kiro Day" da
Plena Alimentos (análise comercial x suprimentos de um frigorífico) — troque os
documentos em ./rules/ pelas regras do seu próprio domínio.

As fontes são os arquivos markdown em ./rules/. Cada arquivo tem front-matter
YAML simples (id, titulo, dominio, cliente, tags) e uma seção de regras extraídas
(RN-XX).

Executado em container (Docker). Localmente: python server.py   (transporte stdio)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from fastmcp import FastMCP

RULES_DIR = Path(__file__).parent / "rules"

mcp = FastMCP("business-rules")


# --------------------------------------------------------------------------- #
# Carregamento e parsing dos documentos de regras
# --------------------------------------------------------------------------- #
@dataclass
class RuleDoc:
    doc_id: str
    path: Path
    meta: dict = field(default_factory=dict)
    body: str = ""

    @property
    def titulo(self) -> str:
        return self.meta.get("titulo", self.doc_id)

    @property
    def tags(self) -> list[str]:
        return self.meta.get("tags", [])


def _parse_front_matter(text: str) -> tuple[dict, str]:
    """Parser mínimo de front-matter YAML (chave: valor e listas [a, b])."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            meta[key] = [i for i in items if i]
        else:
            meta[key] = value.strip('"').strip("'")
    return meta, body


def _load_docs() -> dict[str, RuleDoc]:
    docs: dict[str, RuleDoc] = {}
    if not RULES_DIR.exists():
        return docs
    for path in sorted(RULES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_front_matter(text)
        doc_id = meta.get("id", path.stem)
        docs[doc_id] = RuleDoc(doc_id=doc_id, path=path, meta=meta, body=body)
    return docs


DOCS = _load_docs()

# Índice de regras extraídas (RN-XX ... até o fim da linha / bloco)
_RN_PATTERN = re.compile(r"\*\*(RN-\d+)\*\*\s*[—-]?\s*(.+?)(?=\n- \*\*RN-|\n##|\Z)", re.DOTALL)


def _extract_rules() -> list[dict]:
    rules: list[dict] = []
    for doc in DOCS.values():
        for match in _RN_PATTERN.finditer(doc.body):
            rules.append(
                {
                    "codigo": match.group(1),
                    "texto": " ".join(match.group(2).split()),
                    "fonte": doc.doc_id,
                }
            )
    return rules


RULES_INDEX = _extract_rules()


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
@mcp.tool()
def list_business_rule_documents() -> list[dict]:
    """Lista os documentos de regras de negócio disponíveis.

    Retorna id, título, domínio e tags de cada documento-fonte.
    """
    return [
        {
            "id": d.doc_id,
            "titulo": d.titulo,
            "dominio": d.meta.get("dominio", ""),
            "cliente": d.meta.get("cliente", ""),
            "tags": d.tags,
        }
        for d in DOCS.values()
    ]


@mcp.tool()
def get_business_rule_document(doc_id: str) -> str:
    """Retorna o conteúdo markdown completo de um documento de regras.

    Args:
        doc_id: identificador do documento (ver list_business_rule_documents).
    """
    doc = DOCS.get(doc_id)
    if not doc:
        disponiveis = ", ".join(DOCS) or "(nenhum)"
        return f"Documento '{doc_id}' não encontrado. Disponíveis: {disponiveis}"
    return doc.body


@mcp.tool()
def list_business_rules() -> list[dict]:
    """Lista as regras de negócio estruturadas (RN-XX) extraídas dos documentos.

    Cada regra traz código, texto e o documento de origem.
    """
    return RULES_INDEX


@mcp.tool()
def search_business_rules(query: str, max_results: int = 8) -> list[dict]:
    """Busca por palavra-chave nos documentos e regras de negócio.

    Faz busca case-insensitive por parágrafo. Útil para o agente consultar
    "o que o negócio define sobre X" antes de decidir design/implementação.

    Args:
        query: termo ou frase a buscar (ex.: "margem", "rendimento de carcaça", "fornecedor").
        max_results: número máximo de trechos retornados.
    """
    q = query.lower().strip()
    if not q:
        return []
    hits: list[dict] = []

    # 1) regras estruturadas
    for rule in RULES_INDEX:
        if q in rule["texto"].lower() or q in rule["codigo"].lower():
            hits.append({"tipo": "regra", "ref": rule["codigo"], "fonte": rule["fonte"], "trecho": rule["texto"]})

    # 2) parágrafos dos documentos
    for doc in DOCS.values():
        for para in re.split(r"\n\s*\n", doc.body):
            if q in para.lower():
                trecho = " ".join(para.split())
                if len(trecho) > 500:
                    trecho = trecho[:500] + " …"
                hits.append({"tipo": "trecho", "ref": doc.doc_id, "fonte": doc.doc_id, "trecho": trecho})

    # de-dup preservando ordem
    seen, unique = set(), []
    for h in hits:
        key = (h["ref"], h["trecho"][:80])
        if key not in seen:
            seen.add(key)
            unique.append(h)
    return unique[:max_results]


@mcp.tool()
def get_acceptance_criteria() -> dict:
    """Retorna o critério de aceite oficial do case (Given/When/Then) e o não-escopo.

    Fonte da verdade para o requirements.md (Gate 1) da fase de Inception.
    Case: Kiro Day — Plena Alimentos. NÃO revela os números do gabarito;
    o aceite é sobre o FORMATO da entrega (3 achados + 1 recomendação).
    """
    return {
        "intent": (
            "Responder à diretoria da Plena Alimentos — onde a empresa ganha e perde "
            "dinheiro (comercial x suprimentos) no período abr–set/2025 — usando os "
            "próprios dados com o Kiro (Python/SQL sobre PostgreSQL), em português, "
            "em até 30 minutos."
        ),
        "given_when_then": {
            "dado": (
                "as tabelas 'plena_comercial_faturamento' e "
                "'plena_suprimentos_compra_gado' carregadas no PostgreSQL"
            ),
            "quando": (
                "a equipe explora as duas frentes (margem por canal/corte/cliente e "
                "perda por região/fornecedor/rendimento) perguntando em português"
            ),
            "entao": (
                "a equipe apresenta exatamente 3 achados — cada um com o número "
                "encontrado — e 1 recomendação (a decisão de segunda-feira), conectando "
                "o lado da venda ao lado da compra"
            ),
            "e": (
                "os achados citam a fonte (canal, corte, cliente, região ou fornecedor) "
                "e os números são descobertos pela própria sala, não fornecidos pronto"
            ),
        },
        "nao_escopo": [
            "Revelar os números do gabarito antes da sala descobrir",
            "Usar planilha ou esperar o time de BI — a análise é no Kiro (Python/SQL)",
            "Projeções/forecast ou dados fora do período abr–set/2025",
            "Recomendar troca de ERP/sistema — o foco é a decisão de negócio",
        ],
        "formato_entrega": {
            "achados": 3,
            "recomendacao": 1,
            "exemplo_achado": "O canal X fatura mais, mas o canal Y é o mais rentável.",
            "exemplo_recomendacao": (
                "Renegociar com o fornecedor Z e revisar o transporte da região W."
            ),
        },
    }


if __name__ == "__main__":
    mcp.run()

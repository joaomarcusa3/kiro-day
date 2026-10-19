"""
Runner de SQL para a análise da Plena (sem psql)
================================================
Executa SQL contra o Postgres usando psycopg e imprime o resultado em tabela.

Conexão via DATABASE_URL.

Uso:
    python query.py "SELECT canal, sum(receita_rs) FROM plena_comercial_faturamento GROUP BY 1"
    python query.py -f analises/minha_consulta.sql
    echo "SELECT 1" | python query.py            # lê SQL do stdin
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg


def _read_sql(argv: list[str]) -> str:
    if len(argv) >= 2 and argv[1] == "-f":
        return Path(argv[2]).read_text(encoding="utf-8")
    if len(argv) >= 2:
        return " ".join(argv[1:])
    return sys.stdin.read()


def _print_table(cols: list[str], rows: list[tuple]) -> None:
    widths = [len(c) for c in cols]
    str_rows = [[("" if v is None else str(v)) for v in r] for r in rows]
    for r in str_rows:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(v))
    line = " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
    print(line)
    print("-+-".join("-" * w for w in widths))
    for r in str_rows:
        print(" | ".join(v.ljust(widths[i]) for i, v in enumerate(r)))
    print(f"\n({len(rows)} linha(s))")


def main() -> None:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("DATABASE_URL não definida.")
    sql = _read_sql(sys.argv).strip()
    if not sql:
        sys.exit('Informe o SQL. Ex.: python query.py "SELECT 1"')

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(sql)
        if cur.description is None:
            print(f"OK ({cur.rowcount} linha(s) afetada(s))")
            return
        cols = [d.name for d in cur.description]
        _print_table(cols, cur.fetchall())


if __name__ == "__main__":
    main()

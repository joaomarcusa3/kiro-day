"""
Carga dos datasets da Plena no Postgres
=======================================
Lê os dois CSVs gerados por generate_datasets.py e carrega em tabelas no
Postgres. Idempotente: recria as tabelas a cada execução (DROP + CREATE + COPY).

Conexão via variável de ambiente DATABASE_URL, ex.:
    postgresql://plena:plena@postgres:5432/plena

Rodar:  python load_to_postgres.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

DATA = Path(__file__).parent / "data"

# Tabela -> (arquivo CSV, DDL das colunas)
TABLES = {
    "plena_comercial_faturamento": (
        "plena_comercial_faturamento.csv",
        """
        venda_id       text,
        data           date,
        mes            text,
        planta         text,
        canal          text,
        cliente        text,
        corte          text,
        quantidade_kg  numeric,
        preco_kg       numeric,
        receita_rs     numeric,
        margem_rs      numeric,
        margem_pct     numeric
        """,
    ),
    "plena_suprimentos_compra_gado": (
        "plena_suprimentos_compra_gado.csv",
        """
        compra_id               text,
        data                    date,
        mes                     text,
        planta                  text,
        regiao_origem           text,
        fornecedor              text,
        cabecas                 integer,
        peso_vivo_kg            numeric,
        peso_carcaca_kg         numeric,
        rendimento_carcaca_pct  numeric,
        perda_kg                numeric,
        motivo_perda            text,
        preco_arroba_rs         numeric,
        custo_total_rs          numeric
        """,
    ),
}


def main() -> None:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("DATABASE_URL não definida (ex.: postgresql://plena:plena@postgres:5432/plena)")

    with psycopg.connect(dsn, autocommit=True) as conn:
        for table, (csv_name, columns) in TABLES.items():
            csv_path = DATA / csv_name
            if not csv_path.exists():
                sys.exit(f"CSV não encontrado: {csv_path}. Rode generate_datasets.py antes.")

            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table}")
                cur.execute(f"CREATE TABLE {table} ({columns})")

                with csv_path.open("r", encoding="utf-8") as f:
                    header = f.readline()  # pula o cabeçalho
                    with cur.copy(
                        f"COPY {table} FROM STDIN WITH (FORMAT csv)"
                    ) as copy:
                        for line in f:
                            copy.write(line)

                cur.execute(f"SELECT count(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"{table}: {count} linhas carregadas")

    print("Carga concluída.")


if __name__ == "__main__":
    main()

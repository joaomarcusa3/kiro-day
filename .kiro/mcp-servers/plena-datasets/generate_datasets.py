"""
Gerador de datasets sintéticos — Kiro Day · Plena Alimentos
============================================================
Gera dois CSVs coerentes com o cenário do workshop para carregar no PostgreSQL:

  - plena_comercial_faturamento.csv  (venda de cortes por canal/cliente)
  - plena_suprimentos_compra_gado.csv (compra de boi por região/fornecedor)

Período: abr–set/2025. Três plantas (Centro-Oeste, Norte, Sudeste),
quatro canais (Atacado, Varejo, Food Service, Exportação).

O "gabarito" (quem é mais rentável, qual região rende pior, qual fornecedor puxa
para baixo) está embutido nos pesos abaixo, mas NÃO é documentado — a sala
descobre explorando. Semente fixa p/ reprodutibilidade.

Rodar:  python generate_datasets.py   (no build/seed via Docker é automático)
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(2025)

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

# --------------------------------------------------------------------------- #
# Dimensões
# --------------------------------------------------------------------------- #
PLANTAS = ["Centro-Oeste", "Norte", "Sudeste"]
CANAIS = ["Atacado", "Varejo", "Food Service", "Exportação"]

# Cortes e seu posicionamento (preço médio R$/kg e margem % "escondida")
# dianteiro = volume alto, margem baixa; nobres = margem alta.
CORTES = {
    "Dianteiro":   {"preco": 22.0, "margem_pct": 0.08},
    "Traseiro":    {"preco": 34.0, "margem_pct": 0.15},
    "Picanha":     {"preco": 79.0, "margem_pct": 0.31},  # puxa rentabilidade
    "Filé Mignon": {"preco": 89.0, "margem_pct": 0.33},  # puxa rentabilidade
    "Costela":     {"preco": 28.0, "margem_pct": 0.11},
    "Carne Moída": {"preco": 24.0, "margem_pct": 0.06},  # volume, margem baixa
}

# Canais: fator de volume e de margem (gabarito escondido)
# Atacado fatura muito mas margem fina; Food Service margem melhor; Exportação alta margem/volume médio.
CANAL_PERFIL = {
    "Atacado":      {"vol": 1.8, "margem_mult": 0.70},  # fatura mais, menos rentável
    "Varejo":       {"vol": 1.0, "margem_mult": 1.05},
    "Food Service": {"vol": 0.9, "margem_mult": 1.25},  # mais rentável
    "Exportação":   {"vol": 1.1, "margem_mult": 1.20},
}

# Clientes: alguns de alto volume/baixa margem, outros o contrário (RN-03)
CLIENTES = {
    "Atacado":      ["Rede BoiBom", "Distrib. Pampa", "Mercado União"],
    "Varejo":       ["SuperFrango", "Açougue Central", "Mercado Dia a Dia"],
    "Food Service": ["Churrascaria Gaúcha", "Rede Burger+", "Hotel Platinum"],
    "Exportação":   ["MeatExport CN", "EuroCarnes", "Gulf Foods"],
}
# clientes "margem" (compram nobres) vs "volume" (compram dianteiro/moída)
CLIENTE_PERFIL_MARGEM = {"Churrascaria Gaúcha", "Hotel Platinum", "EuroCarnes", "Açougue Central"}

# Fornecedores de gado por região (gabarito: Norte rende pior; Fornecedor "Fazenda Serra Azul" puxa p/ baixo)
FORNECEDORES = {
    "Centro-Oeste": ["Fazenda Boa Vista", "Agro Cerrado", "Fazenda Três Rios"],
    "Norte":        ["Fazenda Serra Azul", "Pecuária Rio Verde", "Agro Amazônia"],
    "Sudeste":      ["Fazenda Monte Alto", "Pecuária Vale Verde", "Agro Mantiqueira"],
}
# rendimento base de carcaça por região (kg carcaça / kg vivo) — Norte pior
REND_BASE = {"Centro-Oeste": 0.545, "Norte": 0.505, "Sudeste": 0.535}
# fornecedor problemático
FORN_RUIM = "Fazenda Serra Azul"

MOTIVOS_PERDA = [
    "Transporte (longa distância)",
    "Manejo no embarque",
    "Quebra de resfriamento",
    "Condenação sanitária",
    "Jejum pré-abate inadequado",
]


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


START = date(2025, 4, 1)
END = date(2025, 9, 30)


# --------------------------------------------------------------------------- #
# Dataset 1 — Comercial / Faturamento
# --------------------------------------------------------------------------- #
def gen_comercial() -> None:
    path = OUT / "plena_comercial_faturamento.csv"
    rows = []
    vid = 1
    for d in daterange(START, END):
        # ~ algumas vendas por dia por planta
        for planta in PLANTAS:
            for _ in range(random.randint(3, 7)):
                canal = random.choices(
                    CANAIS, weights=[CANAL_PERFIL[c]["vol"] for c in CANAIS]
                )[0]
                cliente = random.choice(CLIENTES[canal])
                # cliente margem tende a comprar cortes nobres
                if cliente in CLIENTE_PERFIL_MARGEM:
                    corte = random.choices(
                        list(CORTES), weights=[1, 2, 4, 4, 2, 1]
                    )[0]
                else:
                    corte = random.choices(
                        list(CORTES), weights=[4, 3, 1, 1, 3, 4]
                    )[0]
                base = CORTES[corte]
                qtd_kg = round(random.uniform(80, 1200) * CANAL_PERFIL[canal]["vol"], 1)
                preco_kg = round(base["preco"] * random.uniform(0.95, 1.08), 2)
                receita = round(qtd_kg * preco_kg, 2)
                margem_pct = base["margem_pct"] * CANAL_PERFIL[canal]["margem_mult"]
                margem_pct = max(0.01, min(0.5, margem_pct * random.uniform(0.9, 1.1)))
                margem_valor = round(receita * margem_pct, 2)
                rows.append(
                    {
                        "venda_id": f"V{vid:06d}",
                        "data": d.isoformat(),
                        "mes": d.strftime("%Y-%m"),
                        "planta": planta,
                        "canal": canal,
                        "cliente": cliente,
                        "corte": corte,
                        "quantidade_kg": qtd_kg,
                        "preco_kg": preco_kg,
                        "receita_rs": receita,
                        "margem_rs": margem_valor,
                        "margem_pct": round(margem_pct * 100, 2),
                    }
                )
                vid += 1
    _write(path, rows)
    print(f"{path.name}: {len(rows)} linhas")


# --------------------------------------------------------------------------- #
# Dataset 2 — Suprimentos / Compra de Gado
# --------------------------------------------------------------------------- #
def gen_suprimentos() -> None:
    path = OUT / "plena_suprimentos_compra_gado.csv"
    rows = []
    cid = 1
    for d in daterange(START, END):
        for planta in PLANTAS:
            # cada planta compra de 1-2 regiões (simplificado: compra da própria + eventual)
            for _ in range(random.randint(2, 5)):
                regiao = random.choices(PLANTAS, weights=[3, 2, 3])[0]
                fornecedor = random.choice(FORNECEDORES[regiao])
                cabecas = random.randint(18, 60)
                peso_vivo_medio = round(random.uniform(460, 540), 1)
                peso_vivo_total = round(cabecas * peso_vivo_medio, 1)

                rend = REND_BASE[regiao] * random.uniform(0.98, 1.02)
                if fornecedor == FORN_RUIM:
                    rend *= 0.94  # fornecedor problemático
                rend = max(0.46, min(0.57, rend))
                peso_carcaca = round(peso_vivo_total * rend, 1)

                # perda/quebra em kg
                perda_pct = (1 - rend) * random.uniform(0.10, 0.18)
                if fornecedor == FORN_RUIM:
                    perda_pct *= 1.4
                perda_kg = round(peso_vivo_total * perda_pct, 1)

                if regiao == "Norte" or fornecedor == FORN_RUIM:
                    motivo = random.choices(
                        MOTIVOS_PERDA, weights=[5, 3, 2, 2, 3]
                    )[0]
                else:
                    motivo = random.choices(
                        MOTIVOS_PERDA, weights=[2, 2, 2, 1, 1]
                    )[0]

                preco_arroba = round(random.uniform(295, 335), 2)
                arrobas = round(peso_vivo_total / 15, 1)  # 1 @ = 15 kg
                custo_total = round(arrobas * preco_arroba, 2)

                rows.append(
                    {
                        "compra_id": f"C{cid:06d}",
                        "data": d.isoformat(),
                        "mes": d.strftime("%Y-%m"),
                        "planta": planta,
                        "regiao_origem": regiao,
                        "fornecedor": fornecedor,
                        "cabecas": cabecas,
                        "peso_vivo_kg": peso_vivo_total,
                        "peso_carcaca_kg": peso_carcaca,
                        "rendimento_carcaca_pct": round(rend * 100, 2),
                        "perda_kg": perda_kg,
                        "motivo_perda": motivo,
                        "preco_arroba_rs": preco_arroba,
                        "custo_total_rs": custo_total,
                    }
                )
                cid += 1
    _write(path, rows)
    print(f"{path.name}: {len(rows)} linhas")


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    gen_comercial()
    gen_suprimentos()
    print(f"CSVs em: {OUT}")

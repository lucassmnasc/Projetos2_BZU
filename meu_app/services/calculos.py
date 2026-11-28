"""Regras determinísticas do motor de simulação: quantidades e custo base.

Nada aqui usa IA. Dadas as mesmas respostas e o mesmo catálogo, o resultado é sempre igual,
então dá para conferir cada número à mão.

Passo a passo de calcular_base():
1. Quantidade pelas respostas: services/recomendacao.py escolhe os dispositivos do setor
   analisado e uma quantidade mínima (1 por ambiente marcado, nº de máquinas da 18.3 etc.).
2. Quantidade pela área: para dispositivos com cobertura_m2 preenchida no admin,
   quantidade = ceil(área ÷ cobertura). Fica valendo o MAIOR dos dois números.
3. Gateways: cada Bzu Gateway tem 4 portas, então gateways = ceil(endpoints ÷ 4).
   O EP200 precisa ficar a até 2 m do gateway, então nunca há menos gateways que EP200.
4. Custo: quantidade × preco_unitario do catálogo (model Dispositivo), somado em custo_base.
"""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Any, Dict, List

from ..models import Dispositivo
from .recomendacao import GATEWAY, recomendar_dispositivos

CENTAVOS = Decimal("0.01")


def _quantidade_por_area(area_m2: int | None, cobertura_m2: Decimal | None) -> int:
    """Regra do passo 2. Sem área ou sem cobertura cadastrada, a regra não se aplica (0)."""
    if not area_m2 or not cobertura_m2 or cobertura_m2 <= 0:
        return 0
    return math.ceil(Decimal(area_m2) / cobertura_m2)


def calcular_base(respostas: Dict[str, Any]) -> Dict[str, Any]:
    """Recebe as respostas validadas (Simulacao.respostas) e devolve itens, quantidades e custo_base.

    Os valores em R$ saem como float com 2 casas para caberem no JSONField.
    """
    recomendacao = recomendar_dispositivos(respostas)
    area_m2 = respostas.get("area_m2")  # pergunta 10
    catalogo = {d.codigo: d for d in Dispositivo.objects.all()}

    itens: List[Dict[str, Any]] = []
    total_endpoints = 0
    qtd_ep200 = 0

    for rec in recomendacao["dispositivos"]:
        codigo = rec["codigo"]
        cadastro = catalogo.get(codigo)
        qtd_respostas = rec["quantidade_minima"]
        qtd_area = _quantidade_por_area(area_m2, cadastro.cobertura_m2 if cadastro else None)
        quantidade = max(qtd_respostas, qtd_area)

        regra = f"{qtd_respostas} pelas respostas do questionário"
        if qtd_area:
            regra += f"; {qtd_area} pela área ({area_m2} m² ÷ {cadastro.cobertura_m2} m² por dispositivo)"
        itens.append(_item(codigo, rec["nome"], quantidade, cadastro, regra, rec["motivos"]))

        total_endpoints += quantidade
        if codigo == "EP200":
            qtd_ep200 = quantidade

    # Passo 3: gateways
    if total_endpoints:
        gateways = max(math.ceil(total_endpoints / GATEWAY["portas"]), qtd_ep200)
        regra = f"{total_endpoints} endpoints ÷ {GATEWAY['portas']} portas por gateway"
        if qtd_ep200 > math.ceil(total_endpoints / GATEWAY["portas"]):
            regra += "; ajustado para 1 gateway por EP200 (limite de 2 m)"
        itens.append(_item("GATEWAY", GATEWAY["nome"], gateways, catalogo.get("GATEWAY"), regra,
                           ["Concentra os endpoints e envia os dados para a Bzu Cloud."]))

    custo_base = sum((Decimal(str(i["subtotal"])) for i in itens), Decimal("0"))
    precos_definidos = bool(itens) and all(i["preco_definido"] for i in itens)

    return {
        "itens": itens,
        "custo_base": float(custo_base.quantize(CENTAVOS)),
        "precos_definidos": precos_definidos,
        "area_m2": area_m2,
        "lacunas": recomendacao["lacunas"],
    }


def _item(codigo: str, nome: str, quantidade: int, cadastro: Dispositivo | None,
          regra: str, motivos: List[str]) -> Dict[str, Any]:
    """Monta uma linha do orçamento. Sem cadastro no catálogo, o preço conta como 0 (não definido)."""
    preco = cadastro.preco_unitario if cadastro else Decimal("0")
    subtotal = (preco * quantidade).quantize(CENTAVOS)
    return {
        "codigo": codigo,
        "nome": cadastro.nome if cadastro else nome,
        "quantidade": quantidade,
        "preco_unitario": float(preco),
        "subtotal": float(subtotal),
        "preco_definido": preco > 0,
        "regra": regra,
        "motivos": motivos,
    }

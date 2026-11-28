"""Orquestra o motor da simulação: regras → IA → salva o resultado.

Hoje executar_simulacao() roda de forma síncrona, dentro da requisição. O campo Simulacao.status
(pendente → processando → pronta/erro) já permite levar isso para uma fila em segundo plano
(Celery, Django-Q, RQ...) sem mudar a página de resultado, que só lê o status.
"""

from __future__ import annotations

import logging

from django.db import transaction

from ..models import Simulacao
from .calculos import calcular_base
from .ia import IAIndisponivel, gerar_analise

logger = logging.getLogger(__name__)


def reservar_para_execucao(simulacao_id: int) -> bool:
    """Muda pendente → processando de forma atômica. Devolve False se outra requisição já pegou."""
    return bool(
        Simulacao.objects.filter(pk=simulacao_id, status=Simulacao.PENDENTE).update(status=Simulacao.PROCESSANDO)
    )


def executar_simulacao(simulacao: Simulacao) -> Simulacao:
    """Roda as regras e depois a IA, salvando o que der certo.

    - Regras falharam: status "erro", sem resultado (não há o que mostrar).
    - IA falhou: status "erro", mas o resultado guarda o cálculo base para a página mostrar algo.
    - Tudo certo: status "pronta" com base + análise.
    """
    try:
        base = calcular_base(simulacao.respostas)
    except Exception:  # erro de programação ou catálogo quebrado: registra e marca erro
        logger.exception("Falha nas regras da simulação %s", simulacao.pk)
        return _salvar(simulacao, Simulacao.ERRO, None)

    try:
        analise = gerar_analise(simulacao.respostas, base)
    except IAIndisponivel as erro:
        logger.warning("Análise da IA indisponível na simulação %s: %s", simulacao.pk, erro)
        return _salvar(simulacao, Simulacao.ERRO, {"base": base, "analise": None})

    return _salvar(simulacao, Simulacao.PRONTA, {"base": base, "analise": analise})


def _salvar(simulacao: Simulacao, status: str, resultado: dict | None) -> Simulacao:
    with transaction.atomic():
        simulacao.status = status
        simulacao.resultado = resultado
        simulacao.save(update_fields=["status", "resultado"])
    return simulacao

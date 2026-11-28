"""Validação das respostas do questionário enviadas por questionario.js.

As opções aqui espelham PERGUNTAS em questionario.js. Ao mudar uma opção lá, mude aqui também.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

LIMITE_OUTRO = 150
LIMITE_TEXTO = 500

AMBIENTES_FRIO = {"camaras-frias", "freezers", "armazenamento", "producao", "trabalho", "estufas"}

# tipo, opções válidas, valor da opção "outro" (ou None)
PERGUNTAS: Dict[str, tuple] = {
    "segmento": ("multipla", {
        "industria-manufatura", "energia-utilities", "varejo-comercio", "logistica-transporte",
        "agronegocio", "saude-medicina", "alimentacao-cadeia-fria", "edificios-instalacoes",
        "telecomunicacoes", "cidades-setor-publico", "educacao"}, "outro"),
    "conhece-iot": ("unica", {"sim", "nao", "ja-ouvi"}, None),
    "usa-iot": ("unica", {"sim", "nao"}, None),
    "uso-iot": ("unica", {"frequente", "periodico", "manual", "sem-central", "ja-iot", "nenhum", "nao-sei"}, None),
    "porte": ("unica", {"micro", "pequena", "media", "grande"}, None),
    "unidades": ("unica", {"1", "2-5", "6-10", "11-20", "21-50", "51-100", "101-500", "500+"}, None),
    "setor": ("multipla", {
        "energia", "temperatura", "ar", "pressao", "portas", "luminosidade", "gases", "maquinas", "nao-sei"}, "outras"),
    "situacoes": ("multipla", {
        "energia", "desperdicio", "temperatura", "ar", "falhas", "ambientes", "portas", "informacao",
        "condicoes"}, "outro"),
    "funcionarios": ("unica", {
        "1-5", "6-20", "21-50", "51-100", "101-250", "251-500", "501-1000", "1000+"}, None),
    # diagnóstico por setor
    "energia-equipamentos": ("texto", None, None),
    "energia-conta": ("moeda", None, None),
    "energia-dificuldade": ("texto", None, None),
    "energia-setores": ("multipla", AMBIENTES_FRIO, "outro"),
    "temperatura-ambientes": ("multipla", AMBIENTES_FRIO, "outro"),
    "temperatura-finalidade": ("unica", {"alteracoes", "perdas", "conservacao", "ambientais", "conformidade"}, "outro"),
    "ar-variaveis": ("multipla", {"eco2", "voc", "particulas", "geral"}, "outro"),
    "ar-ambientes": ("multipla", {"trabalho", "aula", "comerciais", "industriais", "saude", "armazenamento"}, "outro"),
    "ar-finalidade": ("unica", {"melhorar", "alteracoes", "fontes", "ventilacao", "requisitos"}, "outro"),
    "pressao-ambientes": ("multipla", {"salas-limpas", "hospitalares", "laboratorios", "industriais", "ventilacao"}, "outro"),
    "pressao-finalidade": ("unica", {"garantir", "ventilacao", "alteracoes", "controle"}, "outro"),
    "portas-estruturas": ("multipla", {"camaras-frias", "armazenamento", "restrito", "comuns", "janelas"}, "outro"),
    "portas-motivo": ("unica", {"indevidas", "tempo", "ambientais", "acessos"}, "outro"),
    "luminosidade-ambientes": ("multipla", {"trabalho", "producao", "armazenamento", "estufas", "comerciais"}, "outro"),
    "luminosidade-motivo": ("unica", {"niveis", "variacoes", "condicoes"}, "outro"),
    "gases-ambientes": ("multipla", {
        "industriais", "escritorios", "escolares", "saude", "comerciais", "estoques", "pouca-ventilacao"}, "outro"),
    "gases-substancias": ("multipla", {"eco2", "tvoc", "pm-finas", "pm-suspensas"}, "outro"),
    "gases-objetivo": ("unica", {
        "alteracoes", "fontes", "ventilacao", "qualidade", "emissoes", "requisitos"}, "outro"),
    "maquinas-tipos": ("multipla", {
        "producao", "refrigeracao", "climatizacao", "motores", "bombas", "ventilacao"}, "outro"),
    "maquinas-variaveis": ("multipla", {"energia", "temperatura", "umidade", "ar", "pressao"}, "outro"),
    "maquinas-quantidade": ("unica", {"1", "2-5", "6-10", "11-20", "21-50", "51-100", "100+"}, None),
    "maquinas-objetivo": ("unica", {
        "consumo", "alteracoes", "desempenho", "desperdicios", "falhas", "controle"}, "outro"),
    "outras-local": ("texto", None, None),
    "outras-problema": ("texto", None, None),
}

DIAS = {"seg-sex", "seg-sab", "seg-dom", "todos", "variaveis"}
HORARIOS = {"comercial", "estendido", "continuo", "outro"}

PERGUNTAS_POR_SETOR = {
    "energia": ["energia-equipamentos", "energia-conta", "energia-dificuldade", "energia-setores"],
    "temperatura": ["temperatura-ambientes", "temperatura-finalidade"],
    "ar": ["ar-variaveis", "ar-ambientes", "ar-finalidade"],
    "pressao": ["pressao-ambientes", "pressao-finalidade"],
    "portas": ["portas-estruturas", "portas-motivo"],
    "luminosidade": ["luminosidade-ambientes", "luminosidade-motivo"],
    "gases": ["gases-ambientes", "gases-substancias", "gases-objetivo"],
    "maquinas": ["maquinas-tipos", "maquinas-variaveis", "maquinas-quantidade", "maquinas-objetivo"],
    "outras": ["outras-local", "outras-problema"],
}


class RespostaInvalida(ValueError):
    pass


def _texto(valor: Any, limite: int) -> str:
    return valor.strip()[:limite] if isinstance(valor, str) else ""


def _validar(pid: str, bruto: Any) -> Dict[str, Any]:
    """Devolve a resposta limpa de uma pergunta ou levanta RespostaInvalida."""
    tipo, opcoes, outro = PERGUNTAS[pid]
    r = bruto if isinstance(bruto, dict) else {}

    if tipo == "texto":
        texto = _texto(r.get("valor"), LIMITE_TEXTO)
        if not texto:
            raise RespostaInvalida(pid)
        return {"valor": texto}

    if tipo == "moeda":
        try:
            valor = Decimal(str(r.get("valor"))).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise RespostaInvalida(pid)
        if not (Decimal("0") < valor < Decimal("10000000000")):
            raise RespostaInvalida(pid)
        return {"valor": str(valor)}

    validas = opcoes | ({outro} if outro else set())
    if tipo == "unica":
        valores = [r.get("valor")]
    else:
        valores = r.get("valor") if isinstance(r.get("valor"), list) else []
        valores = list(dict.fromkeys(valores))  # remove repetidos mantendo a ordem
    if not valores or any(v not in validas for v in valores):
        raise RespostaInvalida(pid)

    limpo: Dict[str, Any] = {"valor": valores[0] if tipo == "unica" else valores}
    if outro and outro in valores:
        texto_outro = _texto(r.get("outro"), LIMITE_TEXTO if pid == "setor" else LIMITE_OUTRO)
        if not texto_outro:
            raise RespostaInvalida(pid)
        limpo["outro"] = texto_outro
    return limpo


AREA_MAXIMA_M2 = 1_000_000


def _validar_area(bruto: Any) -> int:
    """Pergunta 10: área aproximada em m², inteiro entre 1 e 1.000.000."""
    valor = (bruto if isinstance(bruto, dict) else {}).get("valor")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor != int(valor):
        raise RespostaInvalida("area")
    if not 1 <= int(valor) <= AREA_MAXIMA_M2:
        raise RespostaInvalida("area")
    return int(valor)


def _validar_horario(bruto: Any) -> Dict[str, Any]:
    r = bruto if isinstance(bruto, dict) else {}
    if r.get("dias") not in DIAS or r.get("horario") not in HORARIOS:
        raise RespostaInvalida("horario")
    limpo = {"dias": r["dias"], "horario": r["horario"]}
    if r["horario"] == "outro":
        limpo["horario_outro"] = _texto(r.get("horario_outro"), LIMITE_OUTRO)
        if not limpo["horario_outro"]:
            raise RespostaInvalida("horario")
    return limpo


def validar_questionario(respostas: Any, setor_analisado: Any) -> Dict[str, Any]:
    """
    Confere o caminho inteiro do questionário e devolve os campos de RespostaQuestionario.
    Levanta RespostaInvalida com o id da primeira pergunta inválida.
    """
    if not isinstance(respostas, dict):
        raise RespostaInvalida("respostas")

    limpo: Dict[str, Dict[str, Any]] = {}
    for pid in ("segmento", "conhece-iot", "usa-iot", "porte", "unidades", "setor", "funcionarios"):
        limpo[pid] = _validar(pid, respostas.get(pid))
    limpo["horario"] = _validar_horario(respostas.get("horario"))
    area_m2 = _validar_area(respostas.get("area"))
    limpo["area"] = {"valor": area_m2}

    usa_iot = limpo["usa-iot"]["valor"] == "sim"
    if usa_iot:
        limpo["uso-iot"] = _validar("uso-iot", respostas.get("uso-iot"))

    setores: List[str] = limpo["setor"]["valor"]
    if "nao-sei" in setores:
        if len(setores) > 1:
            raise RespostaInvalida("setor")
        limpo["situacoes"] = _validar("situacoes", respostas.get("situacoes"))
        candidatos = list(PERGUNTAS_POR_SETOR)  # a sugestão é feita no navegador
    else:
        candidatos = setores
    if setor_analisado not in candidatos or setor_analisado not in PERGUNTAS_POR_SETOR:
        raise RespostaInvalida("prioridade")

    diagnostico = {pid: _validar(pid, respostas.get(pid)) for pid in PERGUNTAS_POR_SETOR[setor_analisado]}
    limpo.update(diagnostico)

    conta: Optional[Decimal] = None
    if "energia-conta" in diagnostico:
        conta = Decimal(diagnostico["energia-conta"]["valor"])

    situacoes = limpo.get("situacoes", {})
    return {
        "segmentos": limpo["segmento"]["valor"],
        "segmento_outro": limpo["segmento"].get("outro", ""),
        "conhece_iot": limpo["conhece-iot"]["valor"],
        "usa_iot": usa_iot,
        "uso_iot": limpo.get("uso-iot", {}).get("valor", ""),
        "porte": limpo["porte"]["valor"],
        "unidades": limpo["unidades"]["valor"],
        "dias_operacao": limpo["horario"]["dias"],
        "horario_operacao": limpo["horario"]["horario"],
        "horario_outro": limpo["horario"].get("horario_outro", ""),
        "setores": setores,
        "setor_outro": limpo["setor"].get("outro", ""),
        "situacoes": situacoes.get("valor", []),
        "situacao_outro": situacoes.get("outro", ""),
        "setor_analisado": setor_analisado,
        "funcionarios": limpo["funcionarios"]["valor"],
        "area_m2": area_m2,
        "conta_energia_mensal": conta,
        "diagnostico": diagnostico,
        "respostas": limpo,
    }

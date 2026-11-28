"""Liga as respostas do questionário aos dispositivos reais da Bzu Tech.

O portfólio abaixo vem das folhas de dados oficiais (rev. outubro/2026):
EP101.1, EP111, EP121, EP200, EP400, EP500, Bzu Gateway V1.4 e Bzu Cloud.
Ao receber a folha de dados de um dispositivo novo, adicione-o em PORTFOLIO e nas regras.

As regras recebem os campos já validados de RespostaQuestionario (ver services/questionario.py).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

PORTFOLIO: Dict[str, Dict[str, Any]] = {
    "EP101": {
        "nome": "Bzu Endpoint EP101.1 — Sensor ambiental",
        "mede": ["Temperatura", "Umidade", "Luminosidade"],
        "limites": "Opera de 0 a +60 °C; até 50 m do gateway.",
    },
    "EP111": {
        "nome": "Bzu Endpoint EP111 — Sonda externa para freezers e câmaras frias",
        "mede": ["Temperatura (−40 a +125 °C)", "Umidade"],
        "limites": "Só a sonda inox entra no ambiente frio; o gabinete fica do lado de fora. Até 50 m do gateway.",
    },
    "EP121": {
        "nome": "Bzu Endpoint EP121 — Ambiente + abertura de porta",
        "mede": ["Porta/janela aberta ou fechada", "Temperatura", "Umidade", "Luminosidade"],
        "limites": "Sensor magnético no batente e ímã na folha; até 50 m do gateway.",
    },
    "EP200": {
        "nome": "Bzu Endpoint EP200 — Monitor de qualidade do ar",
        "mede": ["CO₂ equivalente (eCO₂)", "Compostos orgânicos voláteis (TVOC)",
                 "Material particulado PM1.0 a PM10", "Temperatura", "Umidade"],
        "limites": "Precisa ficar a no máximo 2 m do gateway.",
    },
    "EP400": {
        "nome": "Bzu Endpoint EP400 — Medidor de energia trifásico",
        "mede": ["Tensão e corrente por fase e no neutro", "Potência ativa, reativa e aparente",
                 "Energia acumulada (kWh)", "Frequência da rede"],
        "limites": "Trifásico com neutro, até 100 A por fase e 390 V; instalação por profissional (NR-10).",
    },
    "EP500": {
        "nome": "Bzu Endpoint EP500 — Medidor de pressão diferencial",
        "mede": ["Pressão diferencial (−125 a +125 Pa)"],
        "limites": "Para ar e gases não agressivos; até 50 m do gateway.",
    },
}

GATEWAY = {
    "nome": "Bzu Gateway V1.4",
    "portas": 4,
    "descricao": "Concentrador com 4 portas RJ45, Wi-Fi, MQTT/SNMP, bateria de até 4 h e histórico offline em microSD.",
}

PLATAFORMA = {
    "nome": "Bzu Cloud",
    "descricao": "Dashboards, alertas por e-mail, Telegram ou WhatsApp e relatórios em PDF/CSV.",
}

# Necessidades que nenhum dispositivo das folhas de dados atende.
LACUNA_GASES_ESPECIFICOS = (
    "Gases específicos (CO, amônia, H₂S etc.) não são medidos pelo EP200, que cobre eCO₂, TVOC e partículas. "
    "Avaliar com o comercial."
)
LACUNA_VIBRACAO = (
    "Vibração e manutenção preditiva mecânica não estão no portfólio atual; "
    "o EP400 acompanha o consumo elétrico do equipamento."
)

# Palavras-chave para os campos de texto livre ("Outro" e perguntas 19.x).
PALAVRAS_CHAVE = [
    (("porta", "janela", "abert"), "EP121", "Abertura de portas ou janelas citada na descrição."),
    (("freezer", "câmara fria", "camara fria", "refriger", "congel", "vacina"), "EP111",
     "Ambiente refrigerado citado na descrição."),
    (("energia", "consumo", "elétric", "eletric", "kwh", "tensão", "tensao", "corrente", "disjuntor", "quadro"),
     "EP400", "Consumo ou condição elétrica citada na descrição."),
    (("pressão", "pressao", "filtro", "duto", "sala limpa"), "EP500", "Pressão entre ambientes citada na descrição."),
    (("co2", "ar ", "qualidade do ar", "poeira", "partícula", "particula", "fumaça", "fumaca", "odor", "ventila"),
     "EP200", "Qualidade do ar citada na descrição."),
    (("temperatura", "umidade", "calor", "luz", "ilumina", "luminos"), "EP101",
     "Condição ambiental citada na descrição."),
]

MINIMO_POR_FAIXA = {"1": 1, "2-5": 2, "6-10": 6, "11-20": 11, "21-50": 21, "51-100": 51, "100+": 100}


class _Recomendacao:
    def __init__(self) -> None:
        self.itens: Dict[str, Dict[str, Any]] = {}
        self.lacunas: List[str] = []

    def add(self, codigo: str, motivo: str, quantidade: int = 1) -> None:
        item = self.itens.setdefault(codigo, {"codigo": codigo, **PORTFOLIO[codigo], "motivos": [], "quantidade_minima": 0})
        if motivo not in item["motivos"]:
            item["motivos"].append(motivo)
        item["quantidade_minima"] = max(item["quantidade_minima"], quantidade)

    def texto_livre(self, texto: str) -> bool:
        """Procura dispositivos citados num texto livre. Devolve True se encontrou algum."""
        texto = f" {texto.lower()} "
        achou = False
        for chaves, codigo, motivo in PALAVRAS_CHAVE:
            if any(chave in texto for chave in chaves):
                self.add(codigo, motivo)
                achou = True
        return achou

    def resultado(self, setor: str) -> Dict[str, Any]:
        dispositivos = list(self.itens.values())  # ordem de inclusão: o dispositivo principal do setor vem primeiro
        total = sum(i["quantidade_minima"] for i in dispositivos)
        gateways = max(1, math.ceil(total / GATEWAY["portas"])) if total else 0
        # cada EP200 precisa de um gateway a no máximo 2 m
        if "EP200" in self.itens:
            gateways = max(gateways, self.itens["EP200"]["quantidade_minima"])
        return {
            "setor_analisado": setor,
            "dispositivos": dispositivos,
            "gateway": {**GATEWAY, "quantidade_minima": gateways},
            "plataforma": PLATAFORMA,
            "lacunas": self.lacunas,
            "observacao": "Quantidades mínimas estimadas pelo questionário; a quantidade final é definida na visita técnica.",
        }


def _valor(d: Dict[str, Any], pid: str) -> Any:
    return (d.get(pid) or {}).get("valor")


def _lista(d: Dict[str, Any], pid: str) -> List[str]:
    v = _valor(d, pid)
    return v if isinstance(v, list) else ([v] if v else [])


def _outro(d: Dict[str, Any], pid: str) -> str:
    return (d.get(pid) or {}).get("outro", "")


def _energia(r: _Recomendacao, d: Dict[str, Any]) -> None:
    r.add("EP400", "Medição do consumo e da qualidade da energia por quadro ou circuito.")
    ambientes = _lista(d, "energia-setores")
    if {"camaras-frias", "freezers"} & set(ambientes):
        r.add("EP111", "Refrigeração está entre os maiores gastos: a temperatura interna mostra se o equipamento trabalha além do necessário.")
    if {"armazenamento", "producao", "trabalho", "estufas"} & set(ambientes):
        r.add("EP101", "Temperatura e luminosidade dos ambientes ajudam a explicar o consumo de climatização e iluminação.")


def _temperatura(r: _Recomendacao, d: Dict[str, Any]) -> None:
    ambientes = _lista(d, "temperatura-ambientes")
    frios = [a for a in ambientes if a in ("camaras-frias", "freezers")]
    if frios:
        r.add("EP111", "Câmaras frias e freezers pedem a sonda externa: só ela opera abaixo de 0 °C.", len(frios))
    comuns = [a for a in ambientes if a in ("armazenamento", "producao", "trabalho", "estufas")]
    if comuns:
        r.add("EP101", "Temperatura e umidade dos ambientes de armazenamento, produção ou trabalho.", len(comuns))
    if "outro" in ambientes and not r.texto_livre(_outro(d, "temperatura-ambientes")):
        r.add("EP101", "Temperatura e umidade do ambiente descrito.")
    if _valor(d, "temperatura-finalidade") in ("perdas", "conservacao") and frios:
        r.add("EP121", "Porta aberta é causa comum de perda de temperatura em câmaras frias.", len(frios))


def _ar(r: _Recomendacao, d: Dict[str, Any]) -> None:
    ambientes = [a for a in _lista(d, "ar-ambientes") if a != "outro"] or ["outro"]
    r.add("EP200", "Mede eCO₂, TVOC e partículas (PM1.0 a PM10), além de temperatura e umidade.", len(ambientes))
    if _valor(d, "ar-finalidade") == "ventilacao" or "salas-limpas" in _lista(d, "ar-ambientes"):
        r.add("EP500", "A pressão entre ambientes indica se a ventilação está funcionando.")
    if "outro" in _lista(d, "ar-variaveis"):
        r.lacunas.append(LACUNA_GASES_ESPECIFICOS)


def _pressao(r: _Recomendacao, d: Dict[str, Any]) -> None:
    ambientes = [a for a in _lista(d, "pressao-ambientes") if a != "outro"] or ["outro"]
    r.add("EP500", "Pressão diferencial de ±125 Pa entre ambientes ou entre pontos de um duto.", len(ambientes))
    if {"salas-limpas", "hospitalares", "laboratorios"} & set(ambientes):
        r.add("EP200", "Em salas limpas e áreas críticas, a contagem de partículas complementa a pressurização.")
    if "ventilacao" in ambientes:
        r.add("EP400", "O consumo elétrico dos ventiladores ajuda a identificar filtros saturados.")


def _portas(r: _Recomendacao, d: Dict[str, Any]) -> None:
    estruturas = [e for e in _lista(d, "portas-estruturas") if e != "outro"] or ["outro"]
    r.add("EP121", "Sensor magnético informa porta ou janela aberta/fechada e o tempo aberta.", len(estruturas))
    if "camaras-frias" in estruturas:
        r.add("EP111", "Sonda interna mostra quanto a câmara fria perde de temperatura a cada abertura.")


def _luminosidade(r: _Recomendacao, d: Dict[str, Any]) -> None:
    ambientes = [a for a in _lista(d, "luminosidade-ambientes") if a != "outro"] or ["outro"]
    r.add("EP101", "Mede luminosidade, temperatura e umidade em um só dispositivo.", len(ambientes))


def _gases(r: _Recomendacao, d: Dict[str, Any]) -> None:
    ambientes = [a for a in _lista(d, "gases-ambientes") if a != "outro"] or ["outro"]
    r.add("EP200", "Mede eCO₂, TVOC e partículas PM1.0, PM2.5, PM4.0 e PM10.", len(ambientes))
    if "outro" in _lista(d, "gases-substancias"):
        r.lacunas.append(LACUNA_GASES_ESPECIFICOS)
    if _valor(d, "gases-objetivo") == "ventilacao":
        r.add("EP500", "A pressão diferencial indica se a ventilação está renovando o ar.")


def _maquinas(r: _Recomendacao, d: Dict[str, Any]) -> None:
    qtd = MINIMO_POR_FAIXA.get(_valor(d, "maquinas-quantidade"), 1)
    tipos = set(_lista(d, "maquinas-tipos"))
    variaveis = set(_lista(d, "maquinas-variaveis"))

    if "energia" in variaveis or tipos & {"producao", "motores", "bombas", "ventilacao", "climatizacao"} \
            or _valor(d, "maquinas-objetivo") in ("consumo", "desperdicios"):
        r.add("EP400", "Consumo, potência e tensão por equipamento: mostra quem gasta mais e quando funciona fora do normal.", qtd)
    if "refrigeracao" in tipos:
        r.add("EP111", "Temperatura interna de freezers, câmaras frias e refrigeradores.", qtd)
    if "temperatura" in variaveis or "umidade" in variaveis:
        r.add("EP101", "Temperatura e umidade do ambiente onde os equipamentos operam.")
    if "ar" in variaveis:
        r.add("EP200", "Qualidade do ar ao redor dos equipamentos.")
    if "pressao" in variaveis:
        r.add("EP500", "Pressão diferencial nos sistemas de ventilação e filtragem associados.")
    if _valor(d, "maquinas-objetivo") in ("alteracoes", "falhas", "desempenho"):
        r.lacunas.append(LACUNA_VIBRACAO)
    if "outro" in tipos:
        r.texto_livre(_outro(d, "maquinas-tipos"))


def _outras(r: _Recomendacao, d: Dict[str, Any], setor_outro: str) -> None:
    texto = " ".join([setor_outro, _valor(d, "outras-local") or "", _valor(d, "outras-problema") or ""])
    if not r.texto_livre(texto):
        r.lacunas.append("A necessidade descrita não corresponde a um dispositivo do portfólio; o comercial vai avaliar o caso.")


REGRAS = {
    "energia": _energia, "temperatura": _temperatura, "ar": _ar, "pressao": _pressao, "portas": _portas,
    "luminosidade": _luminosidade, "gases": _gases, "maquinas": _maquinas,
}


def recomendar_dispositivos(campos: Dict[str, Any]) -> Dict[str, Any]:
    """Recebe os campos de RespostaQuestionario e devolve os dispositivos indicados, com o motivo de cada um."""
    r = _Recomendacao()
    setor = campos["setor_analisado"]
    diagnostico = campos.get("diagnostico") or {}

    if setor == "outras":
        _outras(r, diagnostico, campos.get("setor_outro", ""))
    else:
        REGRAS[setor](r, diagnostico)

    # Situações marcadas na 8.1 que fogem do setor analisado viram sugestões complementares.
    situacoes = set(campos.get("situacoes") or [])
    if "portas" in situacoes and setor != "portas":
        r.add("EP121", "Você marcou portas ou janelas abertas indevidamente.")
    if "energia" in situacoes and setor != "energia":
        r.add("EP400", "Você marcou gastos elevados com energia elétrica.")
    if campos.get("situacao_outro"):
        r.texto_livre(campos["situacao_outro"])

    return r.resultado(setor)

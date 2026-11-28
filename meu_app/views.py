"""Views das páginas e APIs da Bizu AI (simulação, chat e relatório PDF)."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict

from django.contrib.auth import authenticate, get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, IntegrityError, transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import DadosConta, MensagemChat, RespostaQuestionario, Simulacao, SimulacaoLead
from .services.catalog import FATOR_COLETA, MODOS_OPERACAO, SEGMENTOS, listar_dispositivos
from .services.chatbot import responder_chat
from .services.questionario import RespostaInvalida, validar_questionario
from .services.recomendacao import recomendar_dispositivos
from .services.roi_engine import analisar_operacao
from .services.simulacao import executar_simulacao, reservar_para_execucao

logger = logging.getLogger(__name__)

SESSAO_SIM = "bzu_ultima_simulacao"
SESSAO_CTX = "bzu_contexto_operacao"
SIM_PADRAO = {"qtd_dispositivos": 80, "segmento": "industria", "coleta_atual": "planilha-manual"}


def _parse_json_body(request: HttpRequest) -> Dict[str, Any]:
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return {}


def _salvar_sessao(request: HttpRequest, simulacao: Dict[str, Any], contexto: Dict[str, Any] | None = None) -> None:
    try:
        request.session[SESSAO_SIM] = simulacao
        request.session[SESSAO_CTX] = contexto if contexto is not None else simulacao["parametros"]
    except DatabaseError:
        pass


def _simulacao_sessao(request: HttpRequest) -> Dict[str, Any]:
    try:
        sim = request.session.get(SESSAO_SIM)
    except DatabaseError:
        sim = None
    return sim or analisar_operacao(SIM_PADRAO)


def _session_id(request: HttpRequest) -> str:
    if not request.session.session_key:
        try:
            request.session.create()
        except DatabaseError:
            return uuid.uuid4().hex[:16]
    return request.session.session_key or uuid.uuid4().hex[:16]


def _opcoes_formulario() -> Dict[str, Any]:
    return {
        "segmentos": [(k, v["rotulo"]) for k, v in SEGMENTOS.items()],
        "modos": [(k, v["rotulo"]) for k, v in MODOS_OPERACAO.items()],
        "coletas": [(k, v["rotulo"]) for k, v in FATOR_COLETA.items()],
    }


# ----------------------------------------------------------------- páginas


def login_page(request: HttpRequest) -> HttpResponse:
    """Autentica usuários usando e-mail e senha."""
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    contexto: Dict[str, Any] = {"next": next_url}

    if request.method == "POST":
        email = str(request.POST.get("email", "")).strip()
        senha = str(request.POST.get("senha", ""))
        contexto["email"] = email

        user = None
        if email and senha:
            try:
                User = get_user_model()
                for candidato in User.objects.filter(email__iexact=email):
                    user = authenticate(request, username=candidato.get_username(), password=senha)
                    if user is not None:
                        break
                if user is None:
                    user = authenticate(request, username=email, password=senha)
            except DatabaseError:
                contexto["erro"] = "Não foi possível validar as credenciais no momento."
                return render(request, "meu_app/login.html", contexto)

        if user is not None:
            auth_login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("home")

        contexto["erro"] = "E-mail ou senha inválidos."

    return render(request, "meu_app/login.html", contexto)


def criar_conta_page(request: HttpRequest) -> HttpResponse:
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    contexto: Dict[str, Any] = {"next": next_url}

    if request.method == "POST":
        nome = str(request.POST.get("nome", "")).strip()
        email = str(request.POST.get("email", "")).strip()
        empresa = str(request.POST.get("empresa", "")).strip()
        senha = str(request.POST.get("senha", ""))
        confirmar_senha = str(request.POST.get("confirmar_senha", ""))
        contexto.update({"nome": nome, "email": email, "empresa": empresa})

        if not nome or len(nome) > 150:
            contexto["erro"] = "Informe um nome com até 150 caracteres."
        elif not empresa or len(empresa) > 150:
            contexto["erro"] = "Informe o nome da empresa com até 150 caracteres."
        elif senha != confirmar_senha:
            contexto["erro"] = "As senhas não conferem."
        else:
            User = get_user_model()
            try:
                validate_email(email)
                validate_password(senha, user=User(username=email, email=email, first_name=nome))
                if User.objects.filter(email__iexact=email).exists():
                    contexto["erro"] = "Este e-mail já está cadastrado."
                    return render(request, "meu_app/conta.html", contexto)

                with transaction.atomic():
                    user = User.objects.create_user(
                        username=uuid.uuid4().hex, email=email, password=senha, first_name=nome
                    )
                    DadosConta.objects.create(usuario=user, nome_empresa=empresa)
                auth_login(request, user)
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect("home")
            except ValidationError as error:
                contexto["erro"] = " ".join(error.messages)
            except IntegrityError:
                contexto["erro"] = "Este e-mail já está cadastrado."
            except DatabaseError:
                contexto["erro"] = "Não foi possível criar a conta no momento."

    return render(request, "meu_app/conta.html", contexto)


@login_required(login_url="login")
def perfil_page(request: HttpRequest) -> HttpResponse:
    return render(request, "meu_app/perfil.html", {"dados_conta": getattr(request.user, "dados_conta", None)})


@require_POST
def logout_page(request: HttpRequest) -> HttpResponse:
    auth_logout(request)
    return redirect("home")


def configurar_page(request: HttpRequest) -> HttpResponse:
    """Link "SOLUÇÃO BZU" do menu: abre o último resultado do usuário ou o questionário."""
    if request.user.is_authenticated:
        ultima = Simulacao.objects.filter(usuario=request.user).first()  # ordering = -criado_em
        if ultima:
            return redirect("resultado", pk=ultima.pk)
    return redirect("questionario")


@login_required(login_url="login")
def resultado_page(request: HttpRequest, pk: int) -> HttpResponse:
    """Página de resultado (configurar.html). Cada usuário só vê as próprias simulações."""
    simulacao = get_object_or_404(Simulacao, pk=pk, usuario=request.user)
    resultado = simulacao.resultado or {}
    return render(
        request,
        "meu_app/configurar.html",
        {
            "simulacao": simulacao,
            "base": resultado.get("base"),
            "analise": resultado.get("analise"),
            "aguardando": simulacao.status in (Simulacao.PENDENTE, Simulacao.PROCESSANDO),
        },
    )


def chat_page(request: HttpRequest):
    try:
        sim = request.session.get(SESSAO_SIM)
    except DatabaseError:
        sim = None
    return render(
        request,
        "meu_app/chat.html",
        {
            "simulacao": sim,
            **_opcoes_formulario(),
        },
    )


# ----------------------------------------------------------------- APIs


@require_POST
def api_questionario(request: HttpRequest) -> JsonResponse:
    """Salva as respostas do questionário do usuário logado. Recebe { respostas, setor_analisado }."""
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Faça login para enviar o questionário."}, status=401)

    payload = _parse_json_body(request)
    try:
        campos = validar_questionario(payload.get("respostas"), payload.get("setor_analisado"))
    except RespostaInvalida as erro:
        return JsonResponse({"erro": "Há respostas faltando ou inválidas.", "pergunta": str(erro)}, status=400)

    recomendacao = recomendar_dispositivos(campos)
    try:
        with transaction.atomic():
            registro = RespostaQuestionario.objects.create(usuario=request.user, recomendacao=recomendacao, **campos)
            # A simulação nasce "pendente"; a página de resultado dispara a execução.
            simulacao = Simulacao.objects.create(
                usuario=request.user, questionario=registro, respostas=_json_seguro(campos)
            )
    except DatabaseError:
        logger.exception("Falha ao salvar questionário do usuário %s", request.user.pk)
        return JsonResponse({"erro": "Não foi possível salvar suas respostas no momento."}, status=503)

    return JsonResponse(
        {
            "id": registro.pk,
            "simulacao_id": simulacao.pk,
            "url_resultado": reverse("resultado", args=[simulacao.pk]),
            "recomendacao": recomendacao,
        },
        status=201,
    )


def _json_seguro(campos: Dict[str, Any]) -> Dict[str, Any]:
    """Decimal não cabe em JSONField: a conta de energia vira texto ("1234.56")."""
    conta = campos.get("conta_energia_mensal")
    return {**campos, "conta_energia_mensal": str(conta) if conta is not None else None}


@require_POST
def api_executar_simulacao(request: HttpRequest, pk: int) -> JsonResponse:
    """Roda o motor da simulação (síncrono, pode levar até ~1 min por causa da busca na web)."""
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Faça login."}, status=401)
    simulacao = get_object_or_404(Simulacao, pk=pk, usuario=request.user)

    # Só uma requisição executa; se a página for recarregada no meio, a outra só espera.
    if reservar_para_execucao(simulacao.pk):
        simulacao.refresh_from_db()
        executar_simulacao(simulacao)
    else:
        simulacao.refresh_from_db()
    return JsonResponse({"status": simulacao.status})


@require_GET
def api_dispositivos(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"dispositivos": listar_dispositivos()})


@csrf_exempt
@require_POST
def api_simular(request: HttpRequest) -> JsonResponse:
    """
    Calcula a simulação (dispositivos, Payback, ROI) a partir dos dados da empresa.
    Resposta rápida e determinística; os textos com Gemini são buscados depois em /api/analises-ia/.
    """
    payload = _parse_json_body(request)
    simulacao = analisar_operacao(payload)
    simulacao["modo_ia"] = "local"
    _salvar_sessao(request, simulacao)

    p, f = simulacao["parametros"], simulacao["financeiro"]
    try:
        SimulacaoLead.objects.create(
            nome=p["responsavel"],
            email=p["email"],
            empresa=p["empresa"],
            telefone=p["telefone"],
            cidade=p["cidade"],
            segmento=p["segmento"],
            coleta_atual=p["coleta_atual"],
            modo_operacao=p["modo_operacao"],
            descricao_operacao=p["descricao_operacao"],
            qtd_dispositivos=p["qtd_dispositivos"],
            endpoint_preferido=p["endpoint_preferido"],
            economia_anual_brl=f["economia_anual_brl"],
            roi_12m_pct=f["roi_12m_pct"],
            payback_meses=f["payback_meses"],
            reducao_energia_pct=f["reducao_energia_pct"],
            resultado_json=simulacao,
        )
    except DatabaseError:
        pass

    return JsonResponse(simulacao)


@csrf_exempt
@require_POST
def api_chat(request: HttpRequest) -> JsonResponse:
    """
    Recebe { mensagem, contexto, historico } e retorna
    { resposta, simulacao, contexto, modo_ia }.
    """
    payload = _parse_json_body(request)
    mensagem = str(payload.get("mensagem", "")).strip()[:4000]
    if not mensagem:
        return JsonResponse({"erro": "Envie uma mensagem válida."}, status=400)

    try:
        contexto_sessao = request.session.get(SESSAO_CTX) or {}
    except DatabaseError:
        contexto_sessao = {}
    contexto_req = payload.get("contexto") if isinstance(payload.get("contexto"), dict) else {}
    historico = payload.get("historico") if isinstance(payload.get("historico"), list) else []

    resposta, simulacao, contexto, modo_ia = responder_chat(
        mensagem=mensagem, contexto={**contexto_sessao, **contexto_req}, historico=historico
    )
    if simulacao is not None:
        _salvar_sessao(request, simulacao, contexto)
    else:
        try:
            request.session[SESSAO_CTX] = contexto
        except DatabaseError:
            pass

    try:
        sid = _session_id(request)
        MensagemChat.objects.bulk_create(
            [
                MensagemChat(session_id=sid, papel="user", conteudo=mensagem, modo_ia=modo_ia),
                MensagemChat(session_id=sid, papel="assistant", conteudo=resposta, modo_ia=modo_ia),
            ]
        )
    except DatabaseError:
        pass

    return JsonResponse({"resposta": resposta, "simulacao": simulacao, "contexto": contexto, "modo_ia": modo_ia})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def relatorio_pdf(request: HttpRequest) -> HttpResponse:
    """
    Baixa o relatório PDF.
    GET: usa a última simulação da sessão. POST: recebe { parametros, analises } do navegador.
    """
    from .services.pdf_report import gerar_pdf, nome_arquivo  # import tardio: só carrega ReportLab quando usado

    if request.method == "POST":
        payload = _parse_json_body(request)
        params = payload.get("parametros") if isinstance(payload.get("parametros"), dict) else {}
        simulacao = analisar_operacao(params) if params else _simulacao_sessao(request)
        analises = payload.get("analises")
        if isinstance(analises, dict):
            for chave in ("economia", "roi", "payback", "eficiencia"):
                if isinstance(analises.get(chave), str) and analises[chave].strip():
                    simulacao["analises"][chave] = analises[chave].strip()[:800]
    else:
        simulacao = _simulacao_sessao(request)

    resposta = HttpResponse(gerar_pdf(simulacao), content_type="application/pdf")
    resposta["Content-Disposition"] = f'attachment; filename="{nome_arquivo(simulacao)}"'
    return resposta

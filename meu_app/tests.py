import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from meu_app.services.chatbot import extrair_parametros_mensagem, responder_chat
from meu_app.services.roi_engine import analisar_operacao


class RoiEngineTests(TestCase):
    def test_analise_basica_autocentro(self):
        res = analisar_operacao(
            {
                "qtd_dispositivos": 40,
                "segmento": "autocentro",
                "coleta_atual": "planilha-manual",
                "custo_energia_mensal": 15000,
            }
        )
        self.assertEqual(res["parametros"]["qtd_dispositivos"], 40)
        self.assertEqual(res["parametros"]["segmento"], "autocentro")
        self.assertEqual(sum(d["quantidade"] for d in res["dispositivos_sugeridos"]), 40)
        self.assertGreater(res["financeiro"]["economia_anual_brl"], 0)
        self.assertGreater(res["financeiro"]["roi_12m_pct"], 0)
        self.assertGreater(res["financeiro"]["payback_meses"], 0)

    def test_endpoint_preferido_lidera_mix(self):
        res = analisar_operacao({"qtd_dispositivos": 100, "endpoint": "EP400"})
        codigos = {d["codigo"]: d["quantidade"] for d in res["dispositivos_sugeridos"]}
        self.assertIn("EP400", codigos)
        self.assertGreaterEqual(codigos["EP400"], 60)


class ChatbotServiceTests(TestCase):
    def test_extracao_parametros_linguagem_natural(self):
        ctx = extrair_parametros_mensagem(
            "Tenho um autocentro com 45 equipamentos, gasto R$ 18 mil de energia e usamos planilha manual"
        )
        self.assertEqual(ctx["segmento"], "autocentro")
        self.assertEqual(ctx["qtd_dispositivos"], 45)
        self.assertEqual(ctx["custo_energia_mensal"], 18000.0)
        self.assertEqual(ctx["coleta_atual"], "planilha-manual")

    def test_responder_chat_local(self):
        resposta, sim, ctx, modo = responder_chat(
            "Opero uma indústria com 80 máquinas e sofro com paradas. Qual o payback e ROI?"
        )
        self.assertIn("Payback", resposta)
        self.assertIn("ROI", resposta)
        self.assertEqual(sim["parametros"]["qtd_dispositivos"], 80)
        self.assertEqual(ctx["segmento"], "industria")
        self.assertIn(modo, ("local", "gemini"))


class ApiViewsTests(TestCase):
    def test_api_dispositivos(self):
        resp = self.client.get(reverse("api_dispositivos"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["dispositivos"]), 4)

    def test_api_simular(self):
        resp = self.client.post(
            reverse("api_simular"),
            data=json.dumps({"dispositivos": 50, "endpoint": "EP300", "coleta_atual": "nao-coletamos"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["parametros"]["qtd_dispositivos"], 50)
        self.assertIn("roi_12m", data["formatado"])

    def test_api_chat(self):
        resp = self.client.post(
            reverse("api_chat"),
            data=json.dumps({"mensagem": "Tenho 30 veículos na frota, quais dispositivos usar?"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("resposta", data)
        self.assertEqual(data["simulacao"]["parametros"]["qtd_dispositivos"], 30)

    def test_chat_inicia_zerado_e_saudacao_nao_preenche(self):
        page = self.client.get(reverse("chat"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "R$ 0")
        self.assertContains(page, "Nenhum dispositivo sugerido ainda")

        resp = self.client.post(
            reverse("api_chat"),
            data=json.dumps({"mensagem": "oi"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.json()["simulacao"])

    def test_relatorio_pdf(self):
        resp = self.client.post(
            reverse("relatorio_pdf"),
            data=json.dumps({
                "parametros": {
                    "empresa": "AutoCenter Recife",
                    "segmento": "autocentro",
                    "modo_operacao": "dois-turnos",
                    "qtd_dispositivos": 40,
                }
            }),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF"))


class LoginViewTests(TestCase):
    def test_home_exibe_opcoes_de_login(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Bzu Cloud")
        self.assertContains(resp, f'href="{reverse("login")}">Simulador Cloud</a>')
        self.assertEqual(resp.content.decode().count(f'href="{reverse("login")}">Iniciar simulação</a>'), 2)

    def test_iniciar_simulacao_leva_usuario_logado_ao_questionario(self):
        user = get_user_model().objects.create_user(
            username="maria", email="maria@bzu.com", password="SenhaForte123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode().count(f'href="{reverse("questionario")}">Iniciar simulação</a>'), 2
        )

    def test_login_get_renderiza_template_e_css(self):
        resp = self.client.get(reverse("login"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "meu_app/css/login.css")
        self.assertContains(resp, "Entrar")
        self.assertContains(resp, f'href="{reverse("conta")}">Criar conta</a>')
        self.assertContains(resp, 'name="email"')
        self.assertContains(resp, 'name="senha"')
        self.assertNotContains(resp, 'name="empresa"')

    def test_login_post_autentica_por_email(self):
        User = get_user_model()
        User.objects.create_user(username="usuario", email="usuario@bzu.com", password="segredo123")
        resp = self.client.post(reverse("login"), {"email": "usuario@bzu.com", "senha": "segredo123"})
        self.assertRedirects(resp, reverse("home"))

    def test_login_post_invalido_exibe_erro(self):
        resp = self.client.post(reverse("login"), {"email": "naoexiste@bzu.com", "senha": "errada"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "E-mail ou senha inválidos.")

    def test_conta_get_exibe_campos_e_estilos(self):
        response = self.client.get(reverse("conta"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "meu_app/css/conta.css")
        for field in ("nome", "email", "empresa", "senha", "confirmar_senha"):
            self.assertContains(response, f'name="{field}"')

    def test_cadastro_cria_usuario_e_salva_dados_da_conta(self):
        resp = self.client.post(
            reverse("conta"),
            {
                "nome": "Maria Silva",
                "email": "nova@bzu.com",
                "empresa": "Bzu Tech",
                "senha": "SenhaForte123!",
                "confirmar_senha": "SenhaForte123!",
            },
        )
        self.assertRedirects(resp, reverse("home"))

        user = get_user_model().objects.get(email="nova@bzu.com")
        dados_conta = user.dados_conta
        self.assertEqual(user.first_name, "Maria Silva")
        self.assertEqual(dados_conta.nome_empresa, "Bzu Tech")
        self.assertTrue(user.check_password("SenhaForte123!"))
        self.assertNotEqual(user.password, "SenhaForte123!")
        self.assertIn("_auth_user_id", self.client.session)
        self.assertContains(self.client.get(reverse("home")), "Maria Silva")
        perfil = self.client.get(reverse("perfil"))
        self.assertContains(perfil, "nova@bzu.com")
        self.assertContains(perfil, "Bzu Tech")

    def test_perfil_exige_login_e_exibe_dados(self):
        response = self.client.get(reverse("perfil"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("login")))

        user = get_user_model().objects.create_user(
            username="maria", first_name="Maria Silva", email="maria@bzu.com", password="SenhaForte123!"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("perfil"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria Silva")
        self.assertContains(response, "maria@bzu.com")
        self.assertContains(response, "Sair")

    def test_sair_desautentica_usuario(self):
        user = get_user_model().objects.create_user(
            username="maria", first_name="Maria Silva", email="maria@bzu.com", password="SenhaForte123!"
        )
        self.client.force_login(user)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(self.client.get(reverse("home")), "LOGIN")

    def test_cadastro_recusa_email_duplicado(self):
        User = get_user_model()
        User.objects.create_user(username="existente", email="ja@bzu.com", password="SenhaForte123!")

        resp = self.client.post(
            reverse("conta"),
            {
                "nome": "Outro Nome",
                "email": "JA@bzu.com",
                "empresa": "Outra empresa",
                "senha": "OutraSenha123!",
                "confirmar_senha": "OutraSenha123!",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Este e-mail já está cadastrado.")
        self.assertEqual(User.objects.count(), 1)

    def test_cadastro_recusa_senha_fraca(self):
        resp = self.client.post(
            reverse("conta"),
            {
                "nome": "Maria Silva",
                "email": "nova@bzu.com",
                "empresa": "Bzu Tech",
                "senha": "123",
                "confirmar_senha": "123",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "password")
        self.assertFalse(get_user_model().objects.filter(email="nova@bzu.com").exists())


    def test_cadastro_exige_dados_completos(self):
        resp = self.client.post(
            reverse("conta"),
            {
                "email": "nova@bzu.com",
                "empresa": "Bzu Tech",
                "senha": "SenhaForte123!",
                "confirmar_senha": "SenhaForte123!",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Informe um nome com até 150 caracteres.")
        self.assertFalse(get_user_model().objects.filter(email="nova@bzu.com").exists())

    def test_cadastro_recusa_senhas_diferentes(self):
        response = self.client.post(
            reverse("conta"),
            {
                "nome": "Maria Silva",
                "email": "nova@bzu.com",
                "empresa": "Bzu Tech",
                "senha": "SenhaForte123!",
                "confirmar_senha": "SenhaDiferente123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "As senhas não conferem.")
        self.assertFalse(get_user_model().objects.filter(email="nova@bzu.com").exists())


class QuestionarioViewTests(TestCase):
    def test_questionario_exige_login(self):
        response = self.client.get(reverse("questionario"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('questionario')}")

    def test_questionario_renderiza_cartao_e_api(self):
        user = get_user_model().objects.create_user(username="q2", email="q2@ex.com", password="SenhaForte!2026")
        self.client.force_login(user)
        response = self.client.get(reverse("questionario"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="corpo-pergunta"')
        self.assertContains(response, f'data-api="{reverse("api_questionario")}"')
        self.assertContains(response, "csrfmiddlewaretoken")


class RecomendacaoDispositivosTests(TestCase):
    """Liga respostas do questionário aos dispositivos reais da Bzu."""

    BASE = {
        "segmento": {"valor": ["alimentacao-cadeia-fria"]},
        "conhece-iot": {"valor": "sim"},
        "usa-iot": {"valor": "nao"},
        "porte": {"valor": "media"},
        "unidades": {"valor": "1"},
        "horario": {"dias": "seg-dom", "horario": "continuo"},
        "funcionarios": {"valor": "21-50"},
        "area": {"valor": 300},
    }

    def recomendar(self, setor_analisado, diagnostico, setor=None):
        from meu_app.services.questionario import validar_questionario
        from meu_app.services.recomendacao import recomendar_dispositivos

        respostas = {**self.BASE, "setor": setor or {"valor": [setor_analisado]}, **diagnostico}
        rec = recomendar_dispositivos(validar_questionario(respostas, setor_analisado))
        return rec, {d["codigo"]: d for d in rec["dispositivos"]}

    def test_camara_fria_usa_sonda_externa(self):
        rec, eps = self.recomendar("temperatura", {
            "temperatura-ambientes": {"valor": ["camaras-frias", "freezers", "armazenamento"]},
            "temperatura-finalidade": {"valor": "perdas"},
        })
        self.assertEqual(eps["EP111"]["quantidade_minima"], 2)
        self.assertIn("EP101", eps)
        self.assertIn("EP121", eps)  # porta aberta causa perda de temperatura
        self.assertEqual(rec["gateway"]["quantidade_minima"], 2)  # 2+1+2 = 5 endpoints / 4 portas

    def test_energia_usa_medidor_trifasico(self):
        _, eps = self.recomendar("energia", {
            "energia-equipamentos": {"valor": "Compressores"},
            "energia-conta": {"valor": 9000},
            "energia-dificuldade": {"valor": "Picos"},
            "energia-setores": {"valor": ["producao"]},
        })
        self.assertIn("EP400", eps)
        self.assertNotIn("EP111", eps)

    def test_qualidade_do_ar_exige_gateway_perto_de_cada_ep200(self):
        rec, eps = self.recomendar("ar", {
            "ar-variaveis": {"valor": ["eco2"]},
            "ar-ambientes": {"valor": ["aula", "trabalho", "comerciais"]},
            "ar-finalidade": {"valor": "melhorar"},
        })
        self.assertEqual(eps["EP200"]["quantidade_minima"], 3)
        self.assertEqual(rec["gateway"]["quantidade_minima"], 3)

    def test_gas_fora_do_portfolio_vira_lacuna(self):
        rec, eps = self.recomendar("gases", {
            "gases-ambientes": {"valor": ["industriais"]},
            "gases-substancias": {"valor": ["outro"], "outro": "Amônia"},
            "gases-objetivo": {"valor": "emissoes"},
        })
        self.assertIn("EP200", eps)
        self.assertTrue(rec["lacunas"])

    def test_maquinas_usa_quantidade_informada(self):
        _, eps = self.recomendar("maquinas", {
            "maquinas-tipos": {"valor": ["motores", "refrigeracao"]},
            "maquinas-variaveis": {"valor": ["energia"]},
            "maquinas-quantidade": {"valor": "6-10"},
            "maquinas-objetivo": {"valor": "consumo"},
        })
        self.assertEqual(eps["EP400"]["quantidade_minima"], 6)
        self.assertEqual(eps["EP111"]["quantidade_minima"], 6)

    def test_texto_livre_encontra_dispositivo(self):
        _, eps = self.recomendar("outras", {
            "outras-local": {"valor": "Depósito de vacinas"},
            "outras-problema": {"valor": "A porta fica aberta e a temperatura sobe"},
        }, setor={"valor": ["outras"], "outro": "Controle de vacinas"})
        self.assertIn("EP111", eps)
        self.assertIn("EP121", eps)


class ApiQuestionarioTests(TestCase):
    def test_salva_respostas_e_devolve_recomendacao(self):
        from meu_app.models import RespostaQuestionario

        user = get_user_model().objects.create_user(username="q", email="q@ex.com", password="SenhaForte!2026")
        self.client.force_login(user)
        respostas = {
            **RecomendacaoDispositivosTests.BASE,
            "setor": {"valor": ["portas"]},
            "portas-estruturas": {"valor": ["camaras-frias", "janelas"]},
            "portas-motivo": {"valor": "tempo"},
        }
        resp = self.client.post(
            reverse("api_questionario"),
            data=json.dumps({"respostas": respostas, "setor_analisado": "portas"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        codigos = [d["codigo"] for d in resp.json()["recomendacao"]["dispositivos"]]
        self.assertIn("EP121", codigos)
        registro = RespostaQuestionario.objects.get(pk=resp.json()["id"])
        self.assertEqual(registro.recomendacao["dispositivos"][0]["codigo"], "EP121")

    def test_exige_login(self):
        resp = self.client.post(reverse("api_questionario"), data="{}", content_type="application/json")
        self.assertEqual(resp.status_code, 401)


# ------------------------------------------------------------------ motor da simulação

from decimal import Decimal  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from unittest import mock  # noqa: E402

from django.test import override_settings  # noqa: E402


def _campos(setor_analisado="temperatura", area=300, **diagnostico):
    """Respostas validadas, como ficam em Simulacao.respostas."""
    from meu_app.services.questionario import validar_questionario

    respostas = {
        **RecomendacaoDispositivosTests.BASE,
        "area": {"valor": area},
        "setor": {"valor": [setor_analisado]},
        **(diagnostico or {
            "temperatura-ambientes": {"valor": ["camaras-frias", "armazenamento"]},
            "temperatura-finalidade": {"valor": "alteracoes"},
        }),
    }
    campos = validar_questionario(respostas, setor_analisado)
    campos["conta_energia_mensal"] = None
    return campos


def _resposta_falsa(texto, stop_reason="end_turn"):
    """Imita a resposta do SDK: só o que ia.py lê (content com blocos e stop_reason)."""
    bloco = SimpleNamespace(type="text", text=texto, citations=None)
    return SimpleNamespace(stop_reason=stop_reason, content=[bloco])


class CalculosTests(TestCase):
    def test_precos_zerados_viram_custo_zero_e_aviso(self):
        from meu_app.services.calculos import calcular_base

        base = calcular_base(_campos())
        self.assertEqual([i["codigo"] for i in base["itens"]], ["EP111", "EP101", "GATEWAY"])
        self.assertEqual(base["custo_base"], 0)
        self.assertFalse(base["precos_definidos"])

    def test_area_e_precos_do_catalogo(self):
        from meu_app.models import Dispositivo
        from meu_app.services.calculos import calcular_base

        Dispositivo.objects.filter(codigo="EP101").update(preco_unitario=Decimal("500"), cobertura_m2=Decimal("100"))
        Dispositivo.objects.filter(codigo="EP111").update(preco_unitario=Decimal("800"))
        Dispositivo.objects.filter(codigo="GATEWAY").update(preco_unitario=Decimal("1500"))

        base = calcular_base(_campos(area=450))
        itens = {i["codigo"]: i for i in base["itens"]}
        self.assertEqual(itens["EP101"]["quantidade"], 5)    # ceil(450 / 100) vence 1 pelas respostas
        self.assertEqual(itens["EP111"]["quantidade"], 1)    # sem cobertura: só as respostas
        self.assertEqual(itens["GATEWAY"]["quantidade"], 2)  # 6 endpoints / 4 portas
        self.assertEqual(base["custo_base"], 5 * 500 + 800 + 2 * 1500)
        self.assertTrue(base["precos_definidos"])


class IATests(TestCase):
    BASE = {"custo_base": 1000.0, "itens": [], "precos_definidos": True}
    JSON_OK = json.dumps({
        "custo_estimado": 1200,
        "faixa_custo": [1000, 1500],
        "justificativa_custo": "Preço de mercado maior.",
        "dispositivos_recomendados": [{"nome": "EP111", "motivo": "Câmara fria"}],
        "riscos": ["Wi-Fi fraco"],
        "resumo": "Resumo.",
        "fontes": [{"titulo": "X", "url": "https://exemplo.com"}, {"url": "javascript:alert(1)"}],
    })

    @override_settings(ANTHROPIC_API_KEY="teste")
    def test_le_json_com_cercas_e_filtra_fontes(self):
        from meu_app.services import ia

        resposta = _resposta_falsa("```json\n" + self.JSON_OK + "\n```")
        with mock.patch.object(ia, "_chamar_api", return_value=resposta):
            analise = ia.gerar_analise(_campos(), self.BASE)
        self.assertEqual(analise["custo_estimado"], 1200)
        self.assertEqual(analise["faixa_custo"], [1000, 1500])
        self.assertEqual([f["url"] for f in analise["fontes"]], ["https://exemplo.com"])

    @override_settings(ANTHROPIC_API_KEY="teste")
    def test_custo_diferente_sem_justificativa_volta_ao_base(self):
        from meu_app.services import ia

        dados = json.loads(self.JSON_OK)
        dados["justificativa_custo"] = ""
        with mock.patch.object(ia, "_chamar_api", return_value=_resposta_falsa(json.dumps(dados))):
            analise = ia.gerar_analise(_campos(), self.BASE)
        self.assertEqual(analise["custo_estimado"], 1000.0)
        self.assertTrue(analise["custo_ajustado_pelo_sistema"])

    @override_settings(ANTHROPIC_API_KEY="teste")
    def test_json_invalido_e_recusa_viram_erro(self):
        from meu_app.services import ia

        for resposta in (_resposta_falsa("sem json aqui"), _resposta_falsa("{}", stop_reason="refusal")):
            with mock.patch.object(ia, "_chamar_api", return_value=resposta):
                with self.assertRaises(ia.IAIndisponivel):
                    ia.gerar_analise(_campos(), self.BASE)

    @override_settings(ANTHROPIC_API_KEY="")
    def test_sem_chave(self):
        from meu_app.services import ia

        with self.assertRaises(ia.IAIndisponivel):
            ia.gerar_analise(_campos(), self.BASE)

    def test_textos_do_usuario_sao_limpos_e_limitados(self):
        from meu_app.services.ia import _mensagem_usuario

        campos = _campos()
        campos["segmento_outro"] = "a\x00b" + "x" * 2000
        msg = _mensagem_usuario(campos, self.BASE)
        self.assertNotIn("\x00", msg)
        self.assertNotIn("x" * 600, msg)


class FluxoSimulacaoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="s", email="s@ex.com", password="SenhaForte!2026")
        self.client.force_login(self.user)

    def enviar_questionario(self):
        respostas = {
            **RecomendacaoDispositivosTests.BASE,
            "setor": {"valor": ["portas"]},
            "portas-estruturas": {"valor": ["janelas"]},
            "portas-motivo": {"valor": "tempo"},
        }
        resp = self.client.post(
            reverse("api_questionario"),
            data=json.dumps({"respostas": respostas, "setor_analisado": "portas"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        return resp.json()

    def executar(self, dados):
        return self.client.post(reverse("api_executar_simulacao", args=[dados["simulacao_id"]]))

    def test_ia_falhando_ainda_mostra_calculo_base(self):
        from meu_app.models import Simulacao

        dados = self.enviar_questionario()
        self.assertContains(self.client.get(dados["url_resultado"]), 'id="aguardando"')  # pendente

        with override_settings(ANTHROPIC_API_KEY=""):  # sem chave: a IA falha
            self.assertEqual(self.executar(dados).json()["status"], Simulacao.ERRO)

        pagina = self.client.get(dados["url_resultado"])
        self.assertContains(pagina, "A análise da Bizu AI não ficou pronta")
        self.assertContains(pagina, "EP121")
        self.assertContains(pagina, "ESTIMATIVA")
        self.assertEqual(Simulacao.objects.get().resultado["base"]["custo_base"], 0)

    def test_ia_ok(self):
        from meu_app.services import ia

        dados = self.enviar_questionario()
        texto = IATests.JSON_OK.replace("1200", "0").replace("[1000, 1500]", "[0, 0]")
        with override_settings(ANTHROPIC_API_KEY="teste"), \
                mock.patch.object(ia, "_chamar_api", return_value=_resposta_falsa(texto)):
            self.assertEqual(self.executar(dados).json()["status"], "pronta")
        pagina = self.client.get(dados["url_resultado"])
        self.assertContains(pagina, "Wi-Fi fraco")
        self.assertContains(pagina, "https://exemplo.com")

    def test_nao_executa_duas_vezes(self):
        from meu_app.models import Simulacao

        dados = self.enviar_questionario()
        Simulacao.objects.filter(pk=dados["simulacao_id"]).update(status=Simulacao.PROCESSANDO)
        with mock.patch("meu_app.views.executar_simulacao") as executar:
            resp = self.executar(dados)
        executar.assert_not_called()
        self.assertEqual(resp.json()["status"], "processando")

    def test_outro_usuario_nao_ve_resultado(self):
        dados = self.enviar_questionario()
        outro = get_user_model().objects.create_user(username="o", email="o@ex.com", password="SenhaForte!2026")
        self.client.force_login(outro)
        self.assertEqual(self.client.get(dados["url_resultado"]).status_code, 404)
        self.assertEqual(self.executar(dados).status_code, 404)

    def test_menu_leva_ao_ultimo_resultado(self):
        dados = self.enviar_questionario()
        resp = self.client.get(reverse("configurar"))
        self.assertRedirects(resp, dados["url_resultado"], fetch_redirect_response=False)

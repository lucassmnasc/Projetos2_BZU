from django.conf import settings
from django.db import models


class DadosConta(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dados_conta"
    )
    nome_empresa = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.nome_empresa


class RespostaQuestionario(models.Model):
    """Respostas do questionário do simulador (perguntas 2 a 19), uma linha por envio."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questionarios"
    )

    # Bloco 1: perfil da empresa
    segmentos = models.JSONField(default=list, blank=True)
    segmento_outro = models.CharField(max_length=150, blank=True)
    conhece_iot = models.CharField(max_length=20)
    usa_iot = models.BooleanField(default=False)
    uso_iot = models.CharField(max_length=20, blank=True)
    porte = models.CharField(max_length=20)
    unidades = models.CharField(max_length=20)

    # Bloco 2: mapeamento da operação
    dias_operacao = models.CharField(max_length=20)
    horario_operacao = models.CharField(max_length=20)
    horario_outro = models.CharField(max_length=150, blank=True)
    setores = models.JSONField(default=list, blank=True)
    setor_outro = models.TextField(blank=True)
    situacoes = models.JSONField(default=list, blank=True)
    situacao_outro = models.CharField(max_length=150, blank=True)
    setor_analisado = models.CharField(max_length=20, db_index=True)

    # Bloco 3: diagnóstico específico
    funcionarios = models.CharField(max_length=20)
    area_m2 = models.PositiveIntegerField(null=True, blank=True)  # pergunta 10
    conta_energia_mensal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    diagnostico = models.JSONField(default=dict, blank=True)

    respostas = models.JSONField(default=dict, blank=True)
    # dispositivos indicados a partir das respostas (services/recomendacao.py)
    recomendacao = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Resposta do questionário"
        verbose_name_plural = "Respostas do questionário"

    def __str__(self) -> str:
        return f"{self.usuario} — {self.setor_analisado} ({self.criado_em:%d/%m/%Y})"


class SimulacaoLead(models.Model):
    """Armazena simulações de ROI/Payback e dados de contato do investidor."""

    nome = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    empresa = models.CharField(max_length=150, blank=True)
    telefone = models.CharField(max_length=40, blank=True)
    cidade = models.CharField(max_length=80, blank=True)

    segmento = models.CharField(max_length=50, default="autocentro")
    coleta_atual = models.CharField(max_length=50, default="planilha-manual")
    modo_operacao = models.CharField(max_length=30, default="comercial")
    descricao_operacao = models.TextField(blank=True)
    qtd_dispositivos = models.PositiveIntegerField(default=80)
    endpoint_preferido = models.CharField(max_length=20, blank=True)

    economia_anual_brl = models.FloatField(default=0.0)
    roi_12m_pct = models.IntegerField(default=0)
    payback_meses = models.FloatField(default=0.0)
    reducao_energia_pct = models.IntegerField(default=0)
    resultado_json = models.JSONField(default=dict, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Simulação de Lead"
        verbose_name_plural = "Simulações de Leads"

    def __str__(self) -> str:
        ident = self.empresa or self.nome or "Visitante"
        return f"{ident} — {self.qtd_dispositivos} disp. (ROI {self.roi_12m_pct}%)"


class MensagemChat(models.Model):
    """Histórico opcional das conversas com a Bizu AI."""

    session_id = models.CharField(max_length=64, db_index=True)
    papel = models.CharField(max_length=20, choices=[("user", "Usuário"), ("assistant", "IA")])
    conteudo = models.TextField()
    modo_ia = models.CharField(max_length=20, default="local")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        verbose_name = "Mensagem do Chat"
        verbose_name_plural = "Mensagens do Chat"

    def __str__(self) -> str:
        return f"[{self.papel}] {self.conteudo[:50]}"


class Dispositivo(models.Model):
    """Catálogo de dispositivos e preços usado pelas regras de cálculo (services/calculos.py).

    Os preços são editados no /admin/. Enquanto preco_unitario for 0, a página de resultado
    avisa que o preço ainda não foi definido.
    """

    # Liga o registro aos dispositivos indicados por services/recomendacao.py (EP101, EP111... e GATEWAY).
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=150)
    categoria = models.CharField(max_length=80)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Área (m²) que um dispositivo cobre. Vazio = o dispositivo não é dimensionado por área
    # (ex.: um EP400 por quadro elétrico, um EP121 por porta).
    cobertura_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ["codigo"]
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"


class Simulacao(models.Model):
    """Uma execução do motor de simulação: respostas de entrada e resultado calculado."""

    PENDENTE, PROCESSANDO, PRONTA, ERRO = "pendente", "processando", "pronta", "erro"
    STATUS = [
        (PENDENTE, "Pendente"),
        (PROCESSANDO, "Processando"),  # evita rodar a IA duas vezes se a página for recarregada
        (PRONTA, "Pronta"),
        (ERRO, "Erro"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="simulacoes"
    )
    questionario = models.ForeignKey(
        RespostaQuestionario, on_delete=models.SET_NULL, null=True, blank=True, related_name="simulacoes"
    )
    respostas = models.JSONField(default=dict)
    resultado = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default=PENDENTE, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Simulação"
        verbose_name_plural = "Simulações"

    def __str__(self) -> str:
        return f"Simulação #{self.pk} ({self.get_status_display()})"

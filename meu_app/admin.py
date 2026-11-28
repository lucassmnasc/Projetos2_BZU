from django.contrib import admin

from .models import Dispositivo, MensagemChat, RespostaQuestionario, Simulacao, SimulacaoLead


@admin.register(RespostaQuestionario)
class RespostaQuestionarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "setor_analisado", "porte", "funcionarios", "conta_energia_mensal", "criado_em")
    list_filter = ("setor_analisado", "porte", "usa_iot", "conhece_iot")
    search_fields = ("usuario__email", "usuario__first_name", "usuario__dados_conta__nome_empresa")
    readonly_fields = ("criado_em",)


@admin.register(SimulacaoLead)
class SimulacaoLeadAdmin(admin.ModelAdmin):
    list_display = (
        "empresa",
        "nome",
        "segmento",
        "qtd_dispositivos",
        "roi_12m_pct",
        "payback_meses",
        "criado_em",
    )
    search_fields = ("nome", "email", "empresa")
    list_filter = ("segmento", "coleta_atual")


@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display = ("session_id", "papel", "modo_ia", "criado_em")
    list_filter = ("papel", "modo_ia")
    search_fields = ("session_id", "conteudo")


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "categoria", "preco_unitario", "cobertura_m2")
    list_editable = ("preco_unitario", "cobertura_m2")  # edite preços direto na lista
    search_fields = ("codigo", "nome", "categoria")


@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "status", "criado_em")
    list_filter = ("status",)
    readonly_fields = ("criado_em",)

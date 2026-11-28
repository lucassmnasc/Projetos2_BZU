"""URL configuration for myproject project."""

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from meu_app import views


def tela(nome):
    return TemplateView.as_view(template_name=f"meu_app/{nome}.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", tela("home"), name="home"),
    path("login/", views.login_page, name="login"),
    path("conta/", views.criar_conta_page, name="conta"),
    path("perfil/", views.perfil_page, name="perfil"),
    path("sair/", views.logout_page, name="logout"),
    path("carregando/", tela("carregando"), name="carregando"),
    path("questionario/", login_required(tela("questionario"), login_url="login"), name="questionario"),
    path("configurar/", views.configurar_page, name="configurar"),
    path("chat/", views.chat_page, name="chat"),
    path("relatorio/pdf/", views.relatorio_pdf, name="relatorio_pdf"),
    # APIs da Bizu AI
    path("api/simular/", views.api_simular, name="api_simular"),
    path("api/chat/", views.api_chat, name="api_chat"),
    path("api/questionario/", views.api_questionario, name="api_questionario"),
    path("resultado/<int:pk>/", views.resultado_page, name="resultado"),
    path("api/simulacao/<int:pk>/executar/", views.api_executar_simulacao, name="api_executar_simulacao"),
    path("api/dispositivos/", views.api_dispositivos, name="api_dispositivos"),
]

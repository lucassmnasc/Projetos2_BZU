"""Cadastra o catálogo inicial de dispositivos Bzu (folhas de dados de outubro/2026).

Preço R$ 0,00 e cobertura vazia de propósito: as folhas de dados não trazem esses valores.
Edite-os no /admin/ (Dispositivos). Enquanto o preço for 0, o resultado avisa que não foi definido.
"""

from django.db import migrations

CATALOGO = [
    ("EP101", "Bzu Endpoint EP101.1 — Sensor ambiental", "Ambiente",
     "Temperatura, umidade e luminosidade. Opera de 0 a +60 °C, até 50 m do gateway."),
    ("EP111", "Bzu Endpoint EP111 — Sonda externa", "Cadeia do frio",
     "Sonda inox de temperatura (−40 a +125 °C) e umidade para freezers e câmaras frias."),
    ("EP121", "Bzu Endpoint EP121 — Ambiente + abertura de porta", "Acesso",
     "Sensor magnético de porta/janela, mais temperatura, umidade e luminosidade."),
    ("EP200", "Bzu Endpoint EP200 — Qualidade do ar", "Qualidade do ar",
     "eCO₂, TVOC, PM1.0 a PM10, temperatura e umidade. Máximo de 2 m do gateway."),
    ("EP400", "Bzu Endpoint EP400 — Medidor de energia trifásico", "Energia",
     "Tensão, corrente, potências e energia por fase. Até 100 A por fase."),
    ("EP500", "Bzu Endpoint EP500 — Pressão diferencial", "Pressão",
     "Pressão diferencial de −125 a +125 Pa entre ambientes ou pontos de duto."),
    ("GATEWAY", "Bzu Gateway V1.4", "Infraestrutura",
     "Concentrador com 4 portas RJ45, Wi-Fi, MQTT/SNMP e bateria de até 4 h."),
]


def cadastrar(apps, schema_editor):
    Dispositivo = apps.get_model("meu_app", "Dispositivo")
    for codigo, nome, categoria, descricao in CATALOGO:
        # get_or_create: não sobrescreve preços que alguém já tenha editado
        Dispositivo.objects.get_or_create(
            codigo=codigo, defaults={"nome": nome, "categoria": categoria, "descricao": descricao}
        )


def remover(apps, schema_editor):
    apps.get_model("meu_app", "Dispositivo").objects.filter(codigo__in=[c[0] for c in CATALOGO]).delete()


class Migration(migrations.Migration):
    dependencies = [("meu_app", "0005_dispositivo_simulacao")]
    operations = [migrations.RunPython(cadastrar, remover)]

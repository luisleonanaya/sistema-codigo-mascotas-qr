import pytest
from empresa.models import PlacaQR


@pytest.mark.django_db
def test_creacion_placa_qr_genera_codigo_automatico():
    placa = PlacaQR.objects.create(
        tipo_mascota="Perro",
        estado="Disponible",
        activo=True,
    )

    assert placa.codigo is not None
    assert placa.codigo.startswith("QR-PERRO-")
    assert placa.estado == "Disponible"
    assert placa.activo is True

import pytest
from datetime import timedelta
from django.utils import timezone

from empresa.forms import (
    PropietarioForm,
    MascotaForm,
    ReporteMascotaEncontradaForm,
)
from empresa.models import PlacaQR


@pytest.mark.django_db
def test_propietario_rechaza_telefono_invalido():
    form = PropietarioForm(
        data={
            "nombre": "Luis Leon",
            "email": "luis@example.com",
            "telefono": "abc",
            "direccion": "Calle de prueba",
            "mostrar_contacto_publico": "on",
        }
    )

    assert not form.is_valid()
    assert "telefono" in form.errors


@pytest.mark.django_db
def test_mascota_rechaza_fecha_futura():
    placa = PlacaQR.objects.create(
        tipo_mascota="Perro",
        estado="Disponible",
        activo=True,
    )

    fecha_futura = timezone.now().date() + timedelta(days=5)

    form = MascotaForm(
        data={
            "placa_qr": str(placa.id),
            "nombre": "Firulais",
            "tipo": "Perro",
            "raza": "Mestizo",
            "fecha_nacimiento": fecha_futura.isoformat(),
            "genero": "Macho",
            "color": "Café",
            "estado_salud": "Bueno",
            "senas_particulares": "Collar rojo",
            "descripcion": "Mascota de prueba",
        }
    )

    assert not form.is_valid()
    assert "fecha_nacimiento" in form.errors


@pytest.mark.django_db
def test_mascota_rechaza_placa_de_otro_tipo():
    placa_gato = PlacaQR.objects.create(
        tipo_mascota="Gato",
        estado="Disponible",
        activo=True,
    )

    form = MascotaForm(
        data={
            "placa_qr": str(placa_gato.id),
            "nombre": "Firulais",
            "tipo": "Perro",
            "raza": "Mestizo",
            "fecha_nacimiento": "2020-01-01",
            "genero": "Macho",
            "color": "Café",
            "estado_salud": "Bueno",
            "senas_particulares": "Collar rojo",
            "descripcion": "Mascota de prueba",
        }
    )

    assert not form.is_valid()


@pytest.mark.django_db
def test_reporte_rechaza_telefono_reportante_invalido():
    form = ReporteMascotaEncontradaForm(
        data={
            "nombre_reportante": "Juan",
            "telefono_reportante": "123",
            "mensaje": "Encontré a la mascota cerca del parque.",
            "referencia_ubicacion": "Parque principal",
            "latitud": "",
            "longitud": "",
        }
    )

    assert not form.is_valid()
    assert "telefono_reportante" in form.errors

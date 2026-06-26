import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from empresa.models import (
    Propietario,
    PlacaQR,
    Mascota,
    ReporteMascotaEncontrada,
)


@pytest.mark.django_db
def test_usuario_puede_reportar_mascota_encontrada(client):
    propietario = Propietario.objects.create(
        nombre="Joaquina Silverio",
        email="joaquina@example.com",
        telefono="5555555555",
        direccion="Dirección de prueba",
        mostrar_contacto_publico=True,
    )

    placa = PlacaQR.objects.create(
        tipo_mascota="Gato",
        estado="Asignada",
        activo=True,
    )

    mascota = Mascota.objects.create(
        propietario=propietario,
        placa_qr=placa,
        nombre="Oliver",
        tipo="Gato",
        raza="Bosque de Noruega",
        fecha_nacimiento="2020-01-01",
        genero="Macho",
        color="Naranja",
        estado_salud="Bueno",
        senas_particulares="Ojos grandes",
        descripcion="Gato de prueba",
    )

    url = reverse("reportar_mascota_encontrada", args=[mascota.id])

    response = client.post(
        url,
        data={
            "nombre_reportante": "Pedro",
            "telefono_reportante": "5555555556",
            "mensaje": "Encontré a la mascota.",
            "referencia_ubicacion": "Frente a la iglesia",
            "latitud": "19.4326000",
            "longitud": "-99.1332000",
        },
    )

    assert response.status_code == 200
    assert ReporteMascotaEncontrada.objects.filter(mascota=mascota).exists()

    reporte = ReporteMascotaEncontrada.objects.get(mascota=mascota)
    assert reporte.nombre_reportante == "Pedro"
    assert reporte.telefono_reportante == "5555555556"
    assert reporte.mensaje == "Encontré a la mascota."
    assert reporte.estado_reporte == "Pendiente"


@pytest.mark.django_db
def test_administrador_puede_cerrar_reporte(client):
    user = User.objects.create_user(
        username="admin_test",
        password="12345"
    )

    propietario = Propietario.objects.create(
        nombre="Luis Leon",
        email="luis_test@example.com",
        telefono="5555555557",
        direccion="Dirección de prueba",
        mostrar_contacto_publico=True,
    )

    placa = PlacaQR.objects.create(
        tipo_mascota="Perro",
        estado="Asignada",
        activo=True,
    )

    mascota = Mascota.objects.create(
        propietario=propietario,
        placa_qr=placa,
        nombre="Max",
        tipo="Perro",
        raza="Mestizo",
        fecha_nacimiento="2020-01-01",
        genero="Macho",
        color="Café",
        estado_salud="Bueno",
        senas_particulares="Collar azul",
        descripcion="Perro de prueba",
    )

    reporte = ReporteMascotaEncontrada.objects.create(
        mascota=mascota,
        nombre_reportante="Pedro",
        telefono_reportante="5555555558",
        mensaje="Encontré a la mascota.",
        referencia_ubicacion="Parque central",
        estado_reporte="Pendiente",
        resultado_reporte="Sin definir",
    )

    client.force_login(user)

    url = reverse("detalle_reporte_mascota", args=[reporte.id])

    response = client.post(
        url,
        data={
            "estado_reporte": "Resuelto",
            "resultado_reporte": "Mascota encontrada",
            "observaciones_cierre": "Se contactó al propietario y la mascota fue recuperada.",
        },
    )

    reporte.refresh_from_db()

    assert response.status_code in [200, 302]
    assert reporte.estado_reporte == "Resuelto"
    assert reporte.resultado_reporte == "Mascota encontrada"
    assert reporte.observaciones_cierre == "Se contactó al propietario y la mascota fue recuperada."
    assert reporte.fecha_cierre is not None
    assert reporte.administrador == user

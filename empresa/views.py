import json
import os

import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import EventoQRForm, MascotaForm, PropietarioForm
from .models import EventoQR, Mascota, Propietario


def inicio(request):
    return render(request, "empresa/inicio.html")


def servicios(request):
    return render(request, "empresa/servicios.html")


def contacto(request):
    if request.method == "POST":
        messages.success(request, "Mensaje recibido correctamente.")
        return redirect("contacto")

    return render(request, "empresa/contacto.html")


@login_required
def admin_panel(request):
    return render(request, "empresa/admin_panel.html")


def listar_propietarios(request):
    propietarios = Propietario.objects.all().order_by("nombre")
    return render(
        request,
        "empresa/listar_propietarios.html",
        {"propietarios": propietarios},
    )


@require_POST
def eliminar_propietario(request, propietario_id):
    propietario = get_object_or_404(Propietario, id=propietario_id)
    propietario.delete()
    messages.success(request, "Propietario eliminado correctamente.")
    return redirect("listar_propietarios")


def registrar_mascota(request):
    if request.method == "POST":
        propietario_form = PropietarioForm(request.POST)
        mascota_form = MascotaForm(request.POST, request.FILES)

        if propietario_form.is_valid() and mascota_form.is_valid():
            propietario = propietario_form.save()
            codigo_qr_seleccionado = request.POST.get("codigo_qr")

            mascota = get_object_or_404(
                Mascota,
                codigo_qr=codigo_qr_seleccionado,
                propietario__isnull=True,
            )

            mascota.propietario = propietario
            mascota.nombre = mascota_form.cleaned_data["nombre"]
            mascota.tipo = mascota_form.cleaned_data["tipo"]
            mascota.raza = mascota_form.cleaned_data["raza"]
            mascota.fecha_nacimiento = mascota_form.cleaned_data["fecha_nacimiento"]
            mascota.genero = mascota_form.cleaned_data["genero"]
            mascota.estado_salud = mascota_form.cleaned_data["estado_salud"]
            mascota.descripcion = mascota_form.cleaned_data["descripcion"]
            mascota.foto = mascota_form.cleaned_data["foto"]
            mascota.save()

            messages.success(request, "Mascota registrada correctamente.")
            return redirect("listar_mascotas")
    else:
        propietario_form = PropietarioForm()
        mascota_form = MascotaForm()

    codigos_qr_disponibles = Mascota.objects.filter(propietario__isnull=True)

    return render(
        request,
        "empresa/registrar_mascota.html",
        {
            "propietario_form": propietario_form,
            "mascota_form": mascota_form,
            "mascotas": codigos_qr_disponibles,
        },
    )


def listar_mascotas(request):
    mascotas = Mascota.objects.select_related("propietario").all().order_by("nombre")
    return render(request, "empresa/listar_mascotas.html", {"mascotas": mascotas})


@require_POST
def borrar_mascota(request, id):
    mascota = get_object_or_404(Mascota, id=id)
    mascota.delete()
    messages.success(request, "Mascota eliminada correctamente.")
    return redirect("listar_mascotas")


def registrar_evento(request):
    if request.method == "POST":
        form = EventoQRForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento registrado correctamente.")
            return redirect("inicio")
    else:
        form = EventoQRForm()

    return render(request, "empresa/registrar_evento.html", {"form": form})


def registrar_evento_qr(request, id):
    mascota = get_object_or_404(Mascota, id=id)
    propietario = mascota.propietario
    latitud = request.GET.get("latitud")
    longitud = request.GET.get("longitud")

    if not propietario:
        return JsonResponse(
            {"error": "La mascota no tiene propietario asignado."},
            status=400,
        )

    if not latitud or not longitud:
        return JsonResponse(
            {"error": "No se proporcionaron coordenadas."},
            status=400,
        )

    EventoQR.objects.create(
        mascota=mascota,
        propietario=propietario,
        latitud=latitud,
        longitud=longitud,
    )

    qr_url = generar_qr_mascota(request, mascota)
    return render(
        request,
        "empresa/detalles_mascota.html",
        {
            "mascota": mascota,
            "qr_url": qr_url,
            "latitud": latitud,
            "longitud": longitud,
        },
    )


@csrf_exempt
@require_POST
def guardar_ubicacion(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)

    try:
        datos = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    latitud = datos.get("latitud")
    longitud = datos.get("longitud")

    if not latitud or not longitud:
        return JsonResponse(
            {"error": "Latitud y longitud son obligatorias."},
            status=400,
        )

    evento = None
    if mascota.propietario:
        evento = EventoQR.objects.create(
            mascota=mascota,
            propietario=mascota.propietario,
            latitud=latitud,
            longitud=longitud,
        )

    return JsonResponse(
        {
            "mensaje": "Ubicación guardada correctamente.",
            "evento_id": evento.id if evento else None,
        },
        status=200,
    )


def detalles_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    latitud = request.GET.get("lat")
    longitud = request.GET.get("lon")
    qr_url = generar_qr_mascota(request, mascota)

    context = {
        "mascota": mascota,
        "qr_url": qr_url,
        "latitud": latitud,
        "longitud": longitud,
    }
    return render(request, "empresa/detalles_mascota.html", context)


def generar_qr_mascota(request, mascota):
    detalles_url = request.build_absolute_uri(
        reverse("detalles_mascota", args=[mascota.id])
    )
    url_con_parametros = f"{detalles_url}?lat={{lat}}&lon={{lon}}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_con_parametros)
    qr.make(fit=True)

    qr_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    qr_filename = f"{mascota.id}.png"
    qr_path = os.path.join(qr_dir, qr_filename)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)

    return f"{settings.MEDIA_URL}qr_codes/{qr_filename}"

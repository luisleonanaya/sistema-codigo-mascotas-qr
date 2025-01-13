# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PropietarioForm, MascotaForm  #
from .forms import EventoQRForm
from .models import Mascota, EventoQR
from django.http import JsonResponse
from django.contrib import messages
from .models import Propietario
from django.views.decorators.http import require_POST
import qrcode
from io import BytesIO
from django.http import HttpResponse
import qrcode
from io import BytesIO
import qrcode
import base64
from django.conf import settings
from django.urls import reverse
import os
import uuid




@csrf_exempt
def guardar_ubicacion(request, mascota_id):
    if request.method == "POST":
        datos = json.loads(request.body)
        latitud = datos.get("latitud")
        longitud = datos.get("longitud")

        # Aquí podrías guardar la ubicación en un modelo asociado
        print(f"Ubicación recibida: {latitud}, {longitud}")  # Solo para pruebas
        return JsonResponse({"mensaje": "Ubicación guardada con éxito"}, status=200)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def admin_panel(request):
    return render(request, 'admin_panel.html')

def eliminar_propietario(request, propietario_id):
    propietario = get_object_or_404(Propietario, id=propietario_id)
    propietario.delete()
    return redirect('listar_propietarios')

def listar_propietarios(request):
    propietarios = Propietario.objects.all()
    return render(request, 'listar_propietarios.html', {'propietarios': propietarios})

#@login_required
def registrar_mascota(request):
    if request.method == 'POST':
        propietario_form = PropietarioForm(request.POST)
        mascota_form = MascotaForm(request.POST, request.FILES)

        if propietario_form.is_valid() and mascota_form.is_valid():
            # Crear o asignar el propietario
            propietario = propietario_form.save()

            # Obtener el código QR seleccionado de la lista desplegable
            codigo_qr_seleccionado = request.POST.get('codigo_qr')
            codigo_qr_obj = get_object_or_404(Mascota, codigo_qr=codigo_qr_seleccionado, propietario__isnull=True)

            # Asociar el propietario al registro de la mascota con el código QR seleccionado
            codigo_qr_obj.propietario = propietario
            codigo_qr_obj.nombre = mascota_form.cleaned_data['nombre']
            codigo_qr_obj.tipo = mascota_form.cleaned_data['tipo']
            codigo_qr_obj.raza = mascota_form.cleaned_data['raza']
            codigo_qr_obj.fecha_nacimiento = mascota_form.cleaned_data['fecha_nacimiento']
            codigo_qr_obj.genero = mascota_form.cleaned_data['genero']
            codigo_qr_obj.estado_salud = mascota_form.cleaned_data['estado_salud']
            codigo_qr_obj.descripcion = mascota_form.cleaned_data['descripcion']
            codigo_qr_obj.foto = mascota_form.cleaned_data['foto']

            # Guardar el registro con los datos actualizados
            codigo_qr_obj.save()

            # Redirigir a la página después del registro exitoso
            return redirect('registrar_mascota')  # Asegúrate de que esta ruta exista
    else:
        propietario_form = PropietarioForm()
        mascota_form = MascotaForm()

    # Obtener los códigos QR disponibles (sin propietario)
    codigos_qr_disponibles = Mascota.objects.filter(propietario__isnull=True)

    return render(request, 'registrar_mascota.html', {
        'propietario_form': propietario_form,
        'mascota_form': mascota_form,
        'mascotas': codigos_qr_disponibles,
    })


def registrar_evento(request):
    if request.method == 'POST':
        form = EventoQRForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la página de inicio o a otro lugar
    else:
        form = EventoQRForm()

    return render(request, 'registrar_evento.html', {'form': form})

def registrar_evento_qr(request, id):
    # Obtener la mascota y su propietario
    mascota = get_object_or_404(Mascota, id=id)
    propietario = mascota.propietario

    # Capturar latitud y longitud desde la solicitud GET
    latitud = request.GET.get('latitud')
    longitud = request.GET.get('longitud')

    # Verificar que se hayan proporcionado coordenadas
    if not latitud or not longitud:
        return JsonResponse({'error': 'No se proporcionaron coordenadas'}, status=400)

    # Crear el evento QR
    evento = EventoQR.objects.create(
        mascota=mascota,
        propietario=propietario,
        latitud=latitud,
        longitud=longitud
    )

    # Opcionalmente, mostrar una página con detalles de la mascota
    return render(request, 'detalles_mascota.html', {'mascota': mascota})

@require_POST
def borrar_mascota(request, id):
    mascota = get_object_or_404(Mascota, id=id)
    mascota.delete()
    return redirect('listar_mascotas')  # Redirige a la lista de mascotas

def listar_mascotas(request):
    # Obtiene todas las mascotas de la base de datos
    mascotas = Mascota.objects.select_related('propietario').all()

    context = {
        'mascotas': mascotas,  # Incluye a las mascotas con su propietario relacionado
    }
    return render(request, 'listar_mascotas.html', context)



def inicio(request):
    return render(request, 'inicio.html')

def servicios(request):
    return render(request, 'servicios.html')

def contacto(request):
    return render(request, 'contacto.html')

"""
def detalles_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)

    # Generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(mascota.codigo_qr)
    qr.make(fit=True)

    # Crear imagen del QR y guardarla en media/qr_codes/
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f'{mascota.codigo_qr}.png')
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    img.save(qr_path)

    context = {
        "mascota": mascota,
        "qr_image_url": f'/media/qr_codes/{mascota.codigo_qr}.png',  # URL relativa al archivo estático
    }
    return render(request, 'detalles_mascota.html', context)
"""



def generar_codigo_qr(mascota_id):
    # Obtener la mascota desde la base de datos
    mascota = get_object_or_404(Mascota, id=mascota_id)

    # Generar el enlace dinámico que apuntará a los detalles de la mascota
    detalles_url = f"http://127.0.0.1:8000{reverse('detalles_mascota', args=[mascota.id])}"

    # Configurar y generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(detalles_url)
    qr.make(fit=True)

    # Crear la imagen del QR y determinar el nombre del archivo
    img = qr.make_image(fill_color="black", back_color="white")
    qr_filename = f"{mascota.nombre}_{mascota.codigo_qr}.png"  # Nombre del archivo
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_filename)

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    # Guardar el QR como archivo PNG
    img.save(qr_path)

    # Devolver la URL relativa del archivo
    qr_url = f"{settings.MEDIA_URL}qr_codes/{qr_filename}"
    return qr_url

def detalles_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)

    # Obtener la ubicación del dispositivo, si está disponible
    latitud = request.GET.get('lat', None)
    longitud = request.GET.get('lon', None)

    # Generar URL para acceder a la mascota, con un endpoint que puede aceptar ubicación
    base_url = request.build_absolute_uri(reverse('detalles_mascota', args=[mascota_id]))
    url_con_parametros = f"{base_url}?lat={{lat}}&lon={{lon}}"  # Aquí se pasan latitud y longitud como parámetros dinámicos

    # Generar el Código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_con_parametros)
    qr.make(fit=True)

    # Crear imagen del QR y guardarla
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f'{mascota.nombre}_{mascota.codigo_qr}.png')
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    img.save(qr_path)

    context = {
        "mascota": mascota,
        "qr_url": f"/media/qr_codes/{mascota.nombre}_{mascota.codigo_qr}.png",
        "latitud": latitud,
        "longitud": longitud,
    }

    return render(request, 'detalles_mascota.html', context)



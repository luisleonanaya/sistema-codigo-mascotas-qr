from django.contrib import admin

from .models import EventoQR, Mascota, Propietario


@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "email", "telefono")
    search_fields = ("nombre", "email", "telefono")


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "raza", "propietario", "codigo_qr")
    list_filter = ("tipo", "genero")
    search_fields = ("nombre", "raza", "codigo_qr", "propietario__nombre")


@admin.register(EventoQR)
class EventoQRAdmin(admin.ModelAdmin):
    list_display = ("id", "mascota", "propietario", "fecha_hora", "latitud", "longitud")
    list_filter = ("fecha_hora",)
    search_fields = ("mascota__nombre", "propietario__nombre")

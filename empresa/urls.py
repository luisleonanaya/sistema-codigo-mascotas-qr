from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("servicios/", views.servicios, name="servicios"),
    path("contacto/", views.contacto, name="contacto"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("mascota/<uuid:mascota_id>/", views.detalles_mascota, name="detalles_mascota"),
    path(
        "mascota/<uuid:mascota_id>/guardar-ubicacion/",
        views.guardar_ubicacion,
        name="guardar_ubicacion",
    ),
    path("borrar-mascota/<uuid:id>/", views.borrar_mascota, name="borrar_mascota"),
    path(
        "eliminar-propietario/<int:propietario_id>/",
        views.eliminar_propietario,
        name="eliminar_propietario",
    ),
    path(
        "mascota/<uuid:id>/registrar-evento/",
        views.registrar_evento_qr,
        name="registrar_evento_qr",
    ),
    path("registrar-mascota/", views.registrar_mascota, name="registrar_mascota"),
    path("listar-mascotas/", views.listar_mascotas, name="listar_mascotas"),
    path("listar-propietarios/", views.listar_propietarios, name="listar_propietarios"),

    path(
        "placas-disponibles/",
        views.placas_disponibles_por_tipo,
        name="placas_disponibles"
    ),
]

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
    path("borrar-mascota/<uuid:mascota_id>/", views.borrar_mascota, name="borrar_mascota"),
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

    path("generar-placas/", views.generar_placas_qr, name="generar_placas_qr"),
    path("listar-placas/", views.listar_placas_qr, name="listar_placas_qr"),
    path("placa/<uuid:placa_id>/", views.detalle_placa_qr, name="detalle_placa_qr"),
    path("placa/<uuid:placa_id>/qr/", views.ver_qr_placa, name="ver_qr_placa"),

    path("placa/<uuid:placa_id>/descargar/", views.descargar_qr_placa, name="descargar_qr_placa"),
    path("imprimir-placas/", views.imprimir_placas_qr, name="imprimir_placas_qr"),
    path("mascota/<uuid:mascota_id>/editar/", views.editar_mascota, name="editar_mascota"),

    path(
        "propietario/<str:propietario_id>/editar/",views.editar_propietario,name="editar_propietario"),

    path("mascota/<uuid:mascota_id>/reportar/",views.reportar_mascota_encontrada,name="reportar_mascota_encontrada"),

    path("reportes-mascotas/",views.listar_reportes_mascota,name="listar_reportes_mascota"),

]

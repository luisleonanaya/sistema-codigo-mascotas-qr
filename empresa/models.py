from django.db import models
from django.utils.timezone import now
import uuid


TIPO_MASCOTA_CHOICES = [
    ("Perro", "Perro"),
    ("Gato", "Gato"),
    ("Otro", "Otro"),
]

GENERO_CHOICES = [
    ("Macho", "Macho"),
    ("Hembra", "Hembra"),
]

ESTADO_PLACA_CHOICES = [
    ("Disponible", "Disponible"),
    ("Asignada", "Asignada"),
]

class Propietario(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField(blank=True, null=True)

    mostrar_contacto_publico = models.BooleanField(
        default=True,
        verbose_name="Mostrar datos de contacto al público"
    )

    fecha_registro = models.DateTimeField(default=now)

    estado = models.CharField(
        max_length=20,
        choices=[
            ("Activo", "Activo"),
            ("Inactivo", "Inactivo"),
        ],
        default="Activo"
    )

    def __str__(self):
        return self.nombre

class PlacaQR(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=255, unique=True, blank=True)
    tipo_mascota = models.CharField(max_length=20, choices=TIPO_MASCOTA_CHOICES)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PLACA_CHOICES,
        default="Disponible"
    )
    fecha_generacion = models.DateTimeField(default=now)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            prefijo = self.tipo_mascota.upper()
            self.codigo = f"QR-{prefijo}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.tipo_mascota} - {self.estado}"


class Mascota(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    propietario = models.ForeignKey(
        Propietario,
        on_delete=models.CASCADE,
        related_name="mascotas",
        null=True,
        blank=True
    )

    placa_qr = models.OneToOneField(
        PlacaQR,
        on_delete=models.PROTECT,
        related_name="mascota",
        null=True,
        blank=True
    )

    nombre = models.CharField(max_length=255, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MASCOTA_CHOICES, null=True, blank=True)
    raza = models.CharField("Raza o especie", max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    estado_salud = models.TextField(blank=True, null=True)
    senas_particulares = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to="mascotas/", blank=True, null=True)
    fecha_registro = models.DateTimeField(default=now)
    estado = models.CharField(max_length=20, default="Activo")

    @property
    def codigo_qr(self):
        if self.placa_qr:
            return self.placa_qr.codigo
        return "Sin placa asignada"

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"


class EventoQR(models.Model):
    id = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="eventos")
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name="eventos")
    fecha_hora = models.DateTimeField(default=now)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evento {self.id} - Mascota: {self.mascota.nombre}"

class ReporteMascotaEncontrada(models.Model):
    ESTADO_REPORTE_CHOICES = [
        ("Pendiente", "Pendiente"),
        ("En seguimiento", "En seguimiento"),
        ("Resuelto", "Resuelto"),
    ]

    id = models.AutoField(primary_key=True)

    # Se conserva por compatibilidad con la estructura anterior.
    # Puede quedar vacío porque ahora el reporte se hará directamente desde la mascota.
    evento = models.ForeignKey(
        "EventoQR",
        on_delete=models.CASCADE,
        related_name="reportes",
        null=True,
        blank=True
    )

    mascota = models.ForeignKey(
        "Mascota",
        on_delete=models.CASCADE,
        related_name="reportes_encontrada",
        null=True,
        blank=True
    )

    administrador = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    nombre_reportante = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    telefono_reportante = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    medio_contacto = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mensaje = models.TextField(
        blank=True,
        null=True
    )

    referencia_ubicacion = models.TextField(
        blank=True,
        null=True,
        help_text="Referencia manual del lugar donde se encontró la mascota."
    )

    latitud = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True
    )

    longitud = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True
    )

    fecha_reporte = models.DateTimeField(default=now)

    estado_reporte = models.CharField(
        max_length=30,
        choices=ESTADO_REPORTE_CHOICES,
        default="Pendiente"
    )

    def tiene_ubicacion(self):
        return self.latitud is not None and self.longitud is not None

    def __str__(self):
        if self.mascota:
            return f"Reporte de {self.mascota.nombre} - {self.estado_reporte}"
        return f"Reporte {self.id} - {self.estado_reporte}"

from django import forms
from django.forms.widgets import DateInput
import re
from django.utils import timezone

from .models import EventoQR, Mascota, PlacaQR, Propietario, ReporteMascotaEncontrada, TIPO_MASCOTA_CHOICES


class EventoQRForm(forms.ModelForm):
    class Meta:
        model = EventoQR
        fields = ["mascota", "propietario", "latitud", "longitud", "notas"]

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ["nombre", "email", "telefono", "direccion", "mostrar_contacto_publico"]
        labels = {
            "nombre": "Nombre del propietario",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "direccion": "Dirección",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == "mostrar_contacto_publico":
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")

        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", nombre):
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")

        return nombre

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if email and Propietario.objects.filter(email__iexact=email).exists():
            # No lo bloqueamos totalmente, porque puede ser un propietario existente.
            # La vista lo reutilizará para evitar duplicados.
            return email

        return email

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()

        telefono_limpio = re.sub(r"\D", "", telefono)

        if len(telefono_limpio) < 10:
            raise forms.ValidationError("El teléfono debe tener al menos 10 dígitos.")

        if len(telefono_limpio) > 15:
            raise forms.ValidationError("El teléfono no debe tener más de 15 dígitos.")

        return telefono_limpio

    def validate_unique(self):
        # Evitamos que Django bloquee correos existentes durante el registro.
        # La vista se encargará de reutilizar el propietario existente.
        pass

class MascotaForm(forms.ModelForm):
    placa_qr = forms.ModelChoiceField(
        queryset=PlacaQR.objects.none(),
        label="Placa QR disponible",
        required=True,
        empty_label="Primero selecciona el tipo de mascota"
    )

    class Meta:
        model = Mascota
        fields = [
            "placa_qr",
            "nombre",
            "tipo",
            "raza",
            "fecha_nacimiento",
            "genero",
            "color",
            "estado_salud",
            "senas_particulares",
            "descripcion",
            "foto",
        ]
        labels = {
            "placa_qr": "Placa QR disponible",
            "nombre": "Nombre de la mascota",
            "tipo": "Tipo de mascota",
            "raza": "Raza o especie",
            "fecha_nacimiento": "Fecha de nacimiento",
            "genero": "Género",
            "color": "Color",
            "estado_salud": "Estado de salud",
            "senas_particulares": "Señas particulares",
            "descripcion": "Descripción",
            "foto": "Foto",
        }
        widgets = {
            "fecha_nacimiento": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tipo = None

        if self.is_bound:
            tipo = self.data.get("tipo")
        elif self.instance and self.instance.pk:
            tipo = self.instance.tipo

        if tipo:
            self.fields["placa_qr"].queryset = PlacaQR.objects.filter(
                tipo_mascota=tipo,
                estado="Disponible",
                activo=True
            ).order_by("codigo")
        else:
            self.fields["placa_qr"].queryset = PlacaQR.objects.none()

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()

        if len(nombre) < 2:
            raise forms.ValidationError("El nombre de la mascota debe tener al menos 2 caracteres.")

        if len(nombre) > 100:
            raise forms.ValidationError("El nombre de la mascota es demasiado largo.")

        return nombre

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")

        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")

        return fecha

    def clean_color(self):
        color = (self.cleaned_data.get("color") or "").strip()

        if color and len(color) < 3:
            raise forms.ValidationError("El color debe tener al menos 3 caracteres.")

        return color

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")

        if foto:
            extensiones_permitidas = [".jpg", ".jpeg", ".png", ".webp"]
            nombre_archivo = foto.name.lower()

            if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                raise forms.ValidationError("La foto debe ser JPG, JPEG, PNG o WEBP.")

            limite_mb = 3
            if foto.size > limite_mb * 1024 * 1024:
                raise forms.ValidationError(f"La foto no debe pesar más de {limite_mb} MB.")

        return foto

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        placa_qr = cleaned_data.get("placa_qr")

        if tipo and placa_qr:
            if placa_qr.tipo_mascota != tipo:
                raise forms.ValidationError(
                    "La placa QR seleccionada no corresponde al tipo de mascota."
                )

            if placa_qr.estado != "Disponible" or not placa_qr.activo:
                raise forms.ValidationError(
                    "La placa QR seleccionada ya no está disponible."
                )

        return cleaned_data

class GenerarPlacasQRForm(forms.Form):
    tipo_mascota = forms.ChoiceField(
        choices=TIPO_MASCOTA_CHOICES,
        label="Tipo de mascota"
    )

    cantidad = forms.IntegerField(
        min_value=1,
        max_value=300,
        label="Cantidad de placas a generar",
        help_text="Puedes generar de 1 a 300 placas por vez."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

class MascotaActualizarForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = [
            "nombre",
            "tipo",
            "raza",
            "fecha_nacimiento",
            "genero",
            "color",
            "estado_salud",
            "senas_particulares",
            "descripcion",
            "foto",
        ]
        labels = {
            "nombre": "Nombre de la mascota",
            "tipo": "Tipo de mascota",
            "raza": "Raza o especie",
            "fecha_nacimiento": "Fecha de nacimiento",
            "genero": "Género",
            "color": "Color",
            "estado_salud": "Estado de salud",
            "senas_particulares": "Señas particulares",
            "descripcion": "Descripción",
            "foto": "Foto",
        }
        widgets = {
            "fecha_nacimiento": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

class ReporteMascotaEncontradaForm(forms.ModelForm):
    class Meta:
        model = ReporteMascotaEncontrada
        fields = [
            "nombre_reportante",
            "telefono_reportante",
            "mensaje",
            "referencia_ubicacion",
            "latitud",
            "longitud",
        ]
        labels = {
            "nombre_reportante": "Tu nombre",
            "telefono_reportante": "Teléfono de contacto",
            "mensaje": "Mensaje",
            "referencia_ubicacion": "Referencia del lugar",
        }
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows": 4}),
            "referencia_ubicacion": forms.Textarea(attrs={"rows": 3}),
            "latitud": forms.HiddenInput(),
            "longitud": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name not in ["latitud", "longitud"]:
                field.widget.attrs.update({"class": "form-control"})

        self.fields["nombre_reportante"].required = False
        self.fields["telefono_reportante"].required = False
        self.fields["mensaje"].required = True
        self.fields["referencia_ubicacion"].required = False
        self.fields["latitud"].required = False
        self.fields["longitud"].required = False

    def clean_telefono_reportante(self):
        telefono = (self.cleaned_data.get("telefono_reportante") or "").strip()

        if not telefono:
            return telefono

        telefono_limpio = re.sub(r"\D", "", telefono)

        if len(telefono_limpio) < 10:
            raise forms.ValidationError("El teléfono debe tener al menos 10 dígitos.")

        if len(telefono_limpio) > 15:
            raise forms.ValidationError("El teléfono no debe tener más de 15 dígitos.")

        return telefono_limpio


from django import forms
from django.forms.widgets import DateInput

from .models import EventoQR, Mascota, PlacaQR, Propietario


class EventoQRForm(forms.ModelForm):
    class Meta:
        model = EventoQR
        fields = ["mascota", "propietario", "latitud", "longitud", "notas"]


class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ["nombre", "email", "telefono", "direccion"]

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")

        if len(telefono) < 10:
            raise forms.ValidationError("El teléfono debe tener al menos 10 dígitos.")

        return telefono

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

        self.fields["raza"].label = "Raza o especie"

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        placa_qr = cleaned_data.get("placa_qr")

        if tipo and placa_qr and placa_qr.tipo_mascota != tipo:
            raise forms.ValidationError(
                "La placa QR seleccionada no corresponde al tipo de mascota."
            )

        return cleaned_data
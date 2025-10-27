# app_libros/forms.py
from django import forms
from .models import Libro
from .models import Reserva
from datetime import date, timedelta


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['nombre', 'genero', 'autor', 'sinopsis', 'fecha_creacion']
        widgets = {
            'fecha_creacion': forms.DateInput(attrs={'type': 'date'}),
            'sinopsis': forms.Textarea(attrs={'rows': 4}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_reserva']
        widgets = {
            'fecha_reserva': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

    def clean_fecha_reserva(self):
        fecha = self.cleaned_data['fecha_reserva']
        hoy = date.today()
        limite = hoy + timedelta(days=14)

        if fecha < hoy:
            raise forms.ValidationError("No puedes reservar para fechas pasadas.")
        if fecha > limite:
            raise forms.ValidationError("Solo puedes reservar dentro de los próximos 14 días.")
        return fecha
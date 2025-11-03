# app_libros/forms.py
from django import forms
from .models import Libro
from .models import Reserva
from datetime import date, timedelta
from django.contrib.auth.models import User, Group


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
        limite = hoy + timedelta(days=120)

        if fecha < hoy:
            raise forms.ValidationError("No puedes reservar para fechas pasadas.")
        if fecha > limite:
            raise forms.ValidationError("Solo puedes reservar dentro de los próximos 120 días.")
        return fecha

GRUPOS_VALIDOS = ["Alumno", "Bibliotecario", "Admin"]

def _ajustar_staff_por_grupos(user):
    # is_staff True si es Admin o Bibliotecario (pueden entrar al admin site si quieres)
    nombres = set(user.groups.values_list("name", flat=True))
    user.is_staff = bool(nombres & {"Admin", "Bibliotecario"})
    # Súper usuario NO se toca aquí; se maneja aparte en admin
    user.save(update_fields=["is_staff"])

class UsuarioCreateForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)
    grupos = forms.ModelMultipleChoiceField(
        label="Grupos/Roles",
        queryset=Group.objects.filter(name__in=GRUPOS_VALIDOS),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "grupos", "password1", "password2"]

    def clean(self):
        c = super().clean()
        if c.get("password1") != c.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        return c

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            user.groups.set(self.cleaned_data["grupos"])
            _ajustar_staff_por_grupos(user)
        return user

class UsuarioUpdateForm(forms.ModelForm):
    password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput, required=False)
    grupos = forms.ModelMultipleChoiceField(
        label="Grupos/Roles",
        queryset=Group.objects.filter(name__in=GRUPOS_VALIDOS),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "grupos", "password1", "password2", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # precargar grupos actuales
        self.fields["grupos"].initial = self.instance.groups.filter(name__in=GRUPOS_VALIDOS)

    def clean(self):
        c = super().clean()
        p1, p2 = c.get("password1"), c.get("password2")
        if p1 or p2:
            if p1 != p2:
                self.add_error("password2", "Las contraseñas no coinciden.")
        return c

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get("password1")
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
            user.groups.set(self.cleaned_data["grupos"])
            _ajustar_staff_por_grupos(user)
        return user

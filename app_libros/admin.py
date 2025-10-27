from django.contrib import admin
from .models import Libro, Reserva

# Register your models here.
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('libro', 'usuario', 'fecha_reserva')
    search_fields = ('libro__nombre', 'usuario__username')
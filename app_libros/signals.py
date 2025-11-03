# app_libros/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

GRUPOS_REQUERIDOS = ["Alumno", "Bibliotecario", "Admin"]

@receiver(post_migrate)
def crear_grupos_por_defecto(sender, **kwargs):
    # Solo corre cuando existen tablas de auth
    for nombre in GRUPOS_REQUERIDOS:
        Group.objects.get_or_create(name=nombre)

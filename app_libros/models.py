from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Libro(models.Model):
    id_libro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    genero = models.CharField(max_length=100, blank=True, null=True)
    autor = models.CharField(max_length=100)
    sinopsis = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=False)

    class Meta:
        db_table = 'libros'
        managed = False

    def __str__(self):
        return self.nombre
    

class Reserva(models.Model):#
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()  # Día para el cual se reserva
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('libro', 'fecha_reserva')  # Evita duplicar reservas del mismo libro en el mismo día
        ordering = ['fecha_reserva']

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.nombre} ({self.fecha_reserva})"
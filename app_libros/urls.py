# app_libros/urls.py
from django.urls import path
from . import views
from .views import login_manual

urlpatterns = [
    path('', views.home, name='home'),
    #path('login/', views.login_view, name='login'),
    path('login/', login_manual, name='login'),


    path('libros/', views.listar_libros, name='libros'),

    path('libros/nuevo/',                  views.libro_crear,        name='libro_crear'),
    path('libros/<int:id_libro>/',         views.libro_detalle,      name='libro_detalle'),
    path('libros/<int:id_libro>/editar/',  views.libro_editar,       name='libro_editar'),
    path('libros/<int:id_libro>/eliminar/',views.libro_eliminar,     name='libro_eliminar'),

    path('libros/<int:id_libro>/reservar/', views.reserva_crear, name='reserva_crear'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),

    path('whoami/', views.whoami),





]

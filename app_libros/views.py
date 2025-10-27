from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.models import Group
from .models import Libro, Reserva
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import LibroForm, ReservaForm



# Create your views here.
def home(request):
    return render(request, 'app_libros/home.html')

def login_view(request):
    return render(request, 'app_libros/login.html')

def es_superuser(user):
    return user.is_authenticated and user.is_superuser

def listar_libros(request):
    q = request.GET.get('q')
    libros = Libro.objects.all()
    if q:
        libros = libros.filter(nombre__icontains=q) | libros.filter(autor__icontains=q)
    return render(request, 'app_libros/libros.html', {'libros': libros})




def libro_detalle(request, id_libro):
    libro = get_object_or_404(Libro, id_libro=id_libro)
    return render(request, 'app_libros/detalles.html', {'libro': libro})

@login_required
@user_passes_test(es_superuser)
def libro_crear(request):
    if request.method == 'POST':
        form = LibroForm(request.POST)
        if form.is_valid():
            libro = form.save()
            messages.success(request, 'Libro creado correctamente.')
            return redirect('libro_detalle', id_libro=libro.id_libro)
    else:
        form = LibroForm()
    return render(request, 'app_libros/libro_form.html', {'form': form, 'modo': 'crear'})

@login_required
@user_passes_test(es_superuser)
def libro_editar(request, id_libro):
    libro = get_object_or_404(Libro, id_libro=id_libro)
    if request.method == 'POST':
        form = LibroForm(request.POST, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado correctamente.')
            return redirect('libro_detalle', id_libro=libro.id_libro)
    else:
        form = LibroForm(instance=libro)
    return render(request, 'app_libros/libro_form.html', {'form': form, 'modo': 'editar', 'libro': libro})


@login_required
@user_passes_test(es_superuser)
def libro_eliminar(request, id_libro):
    libro = get_object_or_404(Libro, id_libro=id_libro)
    if request.method == 'POST':
        nombre = libro.nombre
        libro.delete()
        messages.success(request, f'Libro "{nombre}" eliminado.')
        return redirect('libros')
    # confirmación por GET
    return render(request, 'app_libros/libro_confirm_delete.html', {'libro': libro})

def user_in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

@login_required
def reserva_crear(request, id_libro):
    libro = get_object_or_404(Libro, id_libro=id_libro)
    reservas_existentes = Reserva.objects.filter(libro=libro).values_list('fecha_reserva', flat=True)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha_reserva']

            # Verificar si ya existe una reserva para ese día
            if Reserva.objects.filter(libro=libro, fecha_reserva=fecha).exists():
                messages.error(request, f"El libro ya está reservado para el {fecha}.")
            else:
                Reserva.objects.create(
                    usuario=request.user,
                    libro=libro,
                    fecha_reserva=fecha
                )
                messages.success(request, f"Reserva creada exitosamente para el {fecha}.")
                return redirect('libro_detalle', id_libro=libro.id_libro)
    else:
        form = ReservaForm()

    return render(request, 'app_libros/reserva_form.html', {
        'form': form,
        'libro': libro,
        'reservas_existentes': reservas_existentes
    })

@login_required
def mis_reservas(request):
    reservas = (
        Reserva.objects
        .select_related('libro')               # para evitar N+1
        .filter(usuario=request.user)          # 👈 clave: filtra por usuario actual
        .order_by('fecha_reserva', '-fecha_creacion')
    )
    return render(request, 'app_libros/mis_reservas.html', {'reservas': reservas})


def whoami(request):
    return HttpResponse(f"auth={request.user.is_authenticated}, user={getattr(request.user, 'username', None)}")

from django.contrib.auth import authenticate, login


def login_manual(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','').strip()
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            messages.success(request, 'Sesión iniciada.')
            return redirect('home')
        messages.error(request, 'Usuario o contraseña incorrectos, o usuario inactivo.')
    return render(request, 'app_libros/login.html')
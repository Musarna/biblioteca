# app_libros/views_cuentas.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UsuarioCreateForm, UsuarioUpdateForm

def es_superusuario(u):
    return u.is_authenticated and u.is_superuser

@login_required
@user_passes_test(es_superusuario)
def cuentas_list(request):
    q = request.GET.get("q", "").strip()
    users = User.objects.all().order_by("username")
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) |
            Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    paginator = Paginator(users, 12)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "app_libros/cuentas_list.html", {"page_obj": page_obj, "q": q})

@login_required
@user_passes_test(es_superusuario)
def cuentas_create(request):
    if request.method == "POST":
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("cuentas_list")
    else:
        form = UsuarioCreateForm()
    return render(request, "app_libros/cuentas_form.html", {"form": form, "modo": "crear"})

@login_required
@user_passes_test(es_superusuario)
def cuentas_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser and user != request.user:
        # permitir editar a otro superuser, pero cuidado
        pass
    if request.method == "POST":
        form = UsuarioUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("cuentas_list")
    else:
        form = UsuarioUpdateForm(instance=user)
    return render(request, "app_libros/cuentas_form.html", {"form": form, "modo": "editar", "obj": user})

@login_required
@user_passes_test(es_superusuario)
def cuentas_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect("cuentas_list")
    if request.method == "POST":
        user.delete()
        messages.success(request, "Usuario eliminado.")
        return redirect("cuentas_list")
    return render(request, "app_libros/cuentas_confirm_delete.html", {"obj": user})

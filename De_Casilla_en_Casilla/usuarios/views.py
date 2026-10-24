from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import PermisoForm, UsuarioCreateForm, UsuarioUpdateForm
from .models import Usuario


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


class PermisosGestionablesMixin:
    def get_queryset(self):
        return Permission.objects.exclude(
            content_type__app_label__in=['admin', 'auth', 'contenttypes', 'sessions']
        ).exclude(
            codename__in=[
                'add_user',
                'change_user',
                'delete_user',
                'view_user',
                'add_usuario',
                'change_usuario',
                'delete_usuario',
                'view_usuario',
            ]
        )


class UsuarioListView(StaffOnlyMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'


class UsuarioCreateView(StaffOnlyMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'usuarios/formulario.html'
    success_url = reverse_lazy('lista_usuarios')


class UsuarioUpdateView(StaffOnlyMixin, UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'usuarios/formulario.html'
    success_url = reverse_lazy('lista_usuarios')


class UsuarioDeleteView(StaffOnlyMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_borrado.html'
    success_url = reverse_lazy('lista_usuarios')


class PermisoListView(StaffOnlyMixin, PermisosGestionablesMixin, ListView):
    model = Permission
    template_name = 'permisos/lista.html'
    context_object_name = 'permisos'

class PermisoCreateView(StaffOnlyMixin, CreateView):
    model = Permission
    form_class = PermisoForm
    template_name = 'permisos/formulario.html'
    success_url = reverse_lazy('listar_permisos')


class PermisoUpdateView(StaffOnlyMixin, PermisosGestionablesMixin, UpdateView):
    model = Permission
    form_class = PermisoForm
    template_name = 'permisos/formulario.html'
    success_url = reverse_lazy('listar_permisos')


class PermisoDeleteView(StaffOnlyMixin, PermisosGestionablesMixin, DeleteView):
    model = Permission
    template_name = 'permisos/confirmar_borrado.html'
    success_url = reverse_lazy('listar_permisos')

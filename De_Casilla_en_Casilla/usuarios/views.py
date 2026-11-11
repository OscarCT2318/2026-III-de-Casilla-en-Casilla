from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Usuario
from .forms import RegistroPublicoForm, UsuarioAdminCreationForm, UsuarioUpdateForm


class VerPanelMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.puede_ver_panel

    def handle_no_permission(self):
        return render(self.request, 'usuarios/403.html', status=403)


class CrearUsuarioMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.puede_crear_usuarios
        )

    def handle_no_permission(self):
        return render(self.request, 'usuarios/403.html', status=403)


class SoloAdminMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(
            user, self.panel_permission_attribute, False
        )

    def handle_no_permission(self):
        return render(self.request, 'usuarios/403.html', status=403)

class IniciarSesionView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True 

class RegistroUsuarioView(CreateView):
    template_name = 'usuarios/registro.html'
    form_class = RegistroPublicoForm 
    success_url = reverse_lazy('login')

class PanelUsuariosListView(VerPanelMixin, ListView):
    model = Usuario
    template_name = 'usuarios/panel/lista_usuarios.html'
    context_object_name = 'usuarios'


class PanelInicioView(LoginRequiredMixin, TemplateView):
    def get(self, request):
        if request.user.puede_ver_panel:
            return redirect('panel_usuarios_lista')
        if request.user.puede_crear_usuarios:
            return redirect('panel_usuario_crear')
        return render(request, 'usuarios/403.html', status=403)


class PanelUsuarioCreateView(CrearUsuarioMixin, CreateView):
    model = Usuario
    template_name = 'usuarios/panel/formulario_usuario.html'

    def get_success_url(self):
        if self.request.user.puede_ver_panel:
            return reverse_lazy('panel_usuarios_lista')
        return reverse_lazy('panel_usuario_crear')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario creado correctamente.')
        return response

    def get_form_class(self):
        user = self.request.user
        if user.puede_asignar_permisos_usuarios:
            return UsuarioAdminCreationForm
        return RegistroPublicoForm

class PanelUsuarioUpdateView(SoloAdminMixin, UpdateView):
    model = Usuario
    panel_permission_attribute = "puede_editar_usuarios"
    form_class = UsuarioUpdateForm
    template_name = 'usuarios/panel/formulario_usuario.html'
    success_url = reverse_lazy('panel_usuarios_lista')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.puede_asignar_permisos_usuarios:
            form.fields.pop('user_permissions', None)
        return form


class PanelUsuarioDeleteView(SoloAdminMixin, DeleteView):
    model = Usuario
    panel_permission_attribute = "puede_eliminar_usuarios"
    template_name = 'usuarios/panel/confirmar_borrado.html'
    success_url = reverse_lazy('panel_usuarios_lista')


class PerfilUsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'
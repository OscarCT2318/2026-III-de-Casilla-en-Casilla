# usuarios/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import PerfilUsuarioView
from .views import (
    RegistroUsuarioView, IniciarSesionView, 
    PanelInicioView, PanelUsuariosListView, PanelUsuarioCreateView,
    PanelUsuarioUpdateView, PanelUsuarioDeleteView
)

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', IniciarSesionView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('panel/', PanelInicioView.as_view(), name='panel_inicio'),
    path('panel/usuarios/', PanelUsuariosListView.as_view(), name='panel_usuarios_lista'),
    path('panel/usuarios/nuevo/', PanelUsuarioCreateView.as_view(), name='panel_usuario_crear'),
    path('panel/usuarios/<int:pk>/editar/', PanelUsuarioUpdateView.as_view(), name='panel_usuario_editar'),
    path('panel/usuarios/<int:pk>/eliminar/', PanelUsuarioDeleteView.as_view(), name='panel_usuario_eliminar'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
]
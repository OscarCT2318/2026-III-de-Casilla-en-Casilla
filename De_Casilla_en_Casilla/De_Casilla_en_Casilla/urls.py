from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='inicio'),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='sesion_cerrada'),
        name='cerrar_sesion',
    ),
    path(
        'cuentas/sesion-cerrada/',
        TemplateView.as_view(template_name='usuarios/sesion_cerrada.html'),
        name='sesion_cerrada',
    ),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.UsuarioListView.as_view(), name='lista_usuarios'),
    path('nuevo/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('borrar/<int:pk>/', views.UsuarioDeleteView.as_view(), name='borrar_usuario'),
    path('permisos/', views.PermisoListView.as_view(), name='listar_permisos'),
    path('permisos/nuevo/', views.PermisoCreateView.as_view(), name='crear_permiso'),
    path('permisos/editar/<int:pk>/', views.PermisoUpdateView.as_view(), name='editar_permiso'),
    path('permisos/eliminar/<int:pk>/', views.PermisoDeleteView.as_view(), name='eliminar_permiso'),
]

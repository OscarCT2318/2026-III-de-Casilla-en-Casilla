from django.urls import path
from . import views

app_name = 'preguntas'

urlpatterns = [
    path('', views.lista_preguntas, name='lista_preguntas'),
    path('crear/', views.crear_pregunta, name='crear_pregunta'),
    path('editar/<int:pk>/', views.editar_pregunta, name='editar_pregunta'),
    path('eliminar/<int:pk>/', views.eliminar_pregunta, name='eliminar_pregunta'),
]
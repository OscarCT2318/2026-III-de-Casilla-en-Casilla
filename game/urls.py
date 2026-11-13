from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("configuracion/", views.setup, name="setup"),
    path("juego/<str:level>/", views.play, name="play"),
    path("api/pregunta/", views.question, name="question"),
]

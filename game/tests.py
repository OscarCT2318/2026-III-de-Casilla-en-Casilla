from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario


class GameHomeTests(TestCase):
    def test_home_muestra_enlaces_de_autenticacion_a_visitantes(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("registro"))
        self.assertContains(response, "Iniciar sesión")
        self.assertContains(response, "Registrarse")

    def test_login_redirige_al_home_del_juego(self):
        Usuario.objects.create_user(username="jugador", password="ClaveSegura-123")

        response = self.client.post(
            reverse("login"),
            {"username": "jugador", "password": "ClaveSegura-123"},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_usuario_autenticado_ve_el_boton_de_cerrar_sesion(self):
        usuario = Usuario.objects.create_user(username="jugador")
        self.client.force_login(usuario)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("logout"))
        self.assertContains(response, "Cerrar sesión")

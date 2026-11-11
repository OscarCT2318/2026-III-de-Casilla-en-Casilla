from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class PublicAccountFlowTests(TestCase):
    def test_login_page_is_available(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iniciar sesión")

    def test_user_can_register_with_password_hashing(self):
        response = self.client.post(
            reverse("registro"),
            {
                "username": "ana",
                "email": "ana@example.com",
                "telefono": "5557654321",
                "password1": "ClaveSegura-123",
                "password2": "ClaveSegura-123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = Usuario.objects.get(username="ana")
        self.assertTrue(user.check_password("ClaveSegura-123"))

    def test_user_can_log_in_and_log_out(self):
        Usuario.objects.create_user(
            username="alumno",
            password="ClaveSegura-123",
        )

        login_response = self.client.post(
            reverse("login"),
            {
                "username": "alumno",
                "password": "ClaveSegura-123",
            },
        )

        self.assertRedirects(login_response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

        logout_response = self.client.post(reverse("logout"))

        self.assertRedirects(logout_response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

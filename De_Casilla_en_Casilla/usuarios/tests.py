from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class UsuarioCrudTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='administrador',
            password='ClaveSegura-123',
            email='admin@example.com',
            rol='admin',
            telefono='5551234567',
            is_staff=True,
        )
        self.client.force_login(self.usuario)

    def test_inicio_se_renderiza(self):
        response = self.client.get(reverse('inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'De Casilla en Casilla')
        self.assertContains(response, reverse('lista_usuarios'))

    def test_login_se_renderiza(self):
        self.client.logout()

        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar sesión')

    def test_staff_puede_iniciar_sesion(self):
        self.client.logout()

        response = self.client.post(
            reverse('login'),
            {'username': 'administrador', 'password': 'ClaveSegura-123'},
        )

        self.assertRedirects(response, reverse('inicio'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_gestion_requiere_usuario_staff(self):
        self.client.logout()

        protected_urls = [
            reverse('lista_usuarios'),
            reverse('crear_usuario'),
            reverse('editar_usuario', args=[self.usuario.pk]),
            reverse('borrar_usuario', args=[self.usuario.pk]),
            reverse('listar_permisos'),
            reverse('crear_permiso'),
            reverse('editar_permiso', args=[1]),
            reverse('eliminar_permiso', args=[1]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                for method in (self.client.get, self.client.post):
                    response = method(url)
                    self.assertRedirects(
                        response,
                        f'{reverse("login")}?next={url}',
                        fetch_redirect_response=False,
                    )

    def test_usuario_autenticado_no_staff_no_puede_gestionar(self):
        usuario = Usuario.objects.create_user(
            username='usuario',
            password='ClaveSegura-123',
            rol='admin',
        )
        self.client.force_login(usuario)

        protected_urls = [
            reverse('lista_usuarios'),
            reverse('crear_usuario'),
            reverse('editar_usuario', args=[self.usuario.pk]),
            reverse('borrar_usuario', args=[self.usuario.pk]),
            reverse('listar_permisos'),
            reverse('crear_permiso'),
            reverse('editar_permiso', args=[1]),
            reverse('eliminar_permiso', args=[1]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                for method in (self.client.get, self.client.post):
                    self.assertEqual(method(url).status_code, 403)

    def test_no_se_pueden_modificar_permisos_excluidos_por_id(self):
        permiso = Permission.objects.filter(content_type__app_label='auth').first()
        self.assertIsNotNone(permiso)

        edit_response = self.client.get(
            reverse('editar_permiso', args=[permiso.pk])
        )
        delete_response = self.client.get(
            reverse('eliminar_permiso', args=[permiso.pk])
        )

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)

    def test_lista_muestra_usuarios(self):
        response = self.client.get(reverse('lista_usuarios'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'administrador')
        self.assertContains(response, 'Salir')
        self.assertTemplateUsed(response, 'usuarios/lista.html')

    def test_formulario_de_creacion_muestra_requisitos_y_campos(self):
        response = self.client.get(reverse('crear_usuario'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contraseña')
        self.assertContains(response, 'placeholder="Nombre"')
        self.assertContains(response, 'placeholder="Correo"')
        self.assertContains(response, 'placeholder="Teléfono"')
        self.assertContains(response, 'placeholder="Confirmar contraseña"')

    def test_crear_usuario_guarda_contrasena_cifrada(self):
        response = self.client.post(
            reverse('crear_usuario'),
            {
                'username': 'ana',
                'email': 'ana@example.com',
                'rol': 'usuario',
                'telefono': '5557654321',
                'password1': 'OtraClaveSegura-123',
                'password2': 'OtraClaveSegura-123',
            },
        )

        self.assertRedirects(response, reverse('lista_usuarios'))
        nuevo_usuario = Usuario.objects.get(username='ana')
        self.assertTrue(nuevo_usuario.check_password('OtraClaveSegura-123'))

    def test_editar_usuario_actualiza_datos(self):
        response = self.client.post(
            reverse('editar_usuario', args=[self.usuario.pk]),
            {
                'username': 'admin_actualizado',
                'email': 'actualizado@example.com',
                'rol': 'maestro',
                'telefono': '5550000000',
            },
        )

        self.assertRedirects(response, reverse('lista_usuarios'))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.username, 'admin_actualizado')
        self.assertEqual(self.usuario.rol, 'maestro')

    def test_eliminar_usuario_requiere_confirmacion_post(self):
        usuario = Usuario.objects.create_user(username='para_borrar')
        url = reverse('borrar_usuario', args=[usuario.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/confirmar_borrado.html')
        self.assertTrue(Usuario.objects.filter(pk=usuario.pk).exists())

        response = self.client.post(url)

        self.assertRedirects(response, reverse('lista_usuarios'))
        self.assertFalse(Usuario.objects.filter(pk=usuario.pk).exists())

    def test_cerrar_sesion_redirige_a_confirmacion(self):
        response = self.client.post(reverse('cerrar_sesion'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('sesion_cerrada'))
        self.assertTemplateUsed(response, 'usuarios/sesion_cerrada.html')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_lista_permisos_se_renderiza(self):
        response = self.client.get(reverse('listar_permisos'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permisos/lista.html')

    def test_formularios_de_permisos_se_renderizan(self):
        create_response = self.client.get(reverse('crear_permiso'))
        content_type = ContentType.objects.create(
            app_label='testapp',
            model='managedpermission',
        )
        permiso = Permission.objects.create(
            name='Permiso de prueba',
            codename='test_permission',
            content_type=content_type,
        )

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(
            self.client.get(reverse('editar_permiso', args=[permiso.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('eliminar_permiso', args=[permiso.pk])).status_code,
            200,
        )

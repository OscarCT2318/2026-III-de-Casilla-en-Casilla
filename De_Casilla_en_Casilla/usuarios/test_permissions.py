from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from .forms import (
    RegistroPublicoForm,
    UsuarioAdminCreationForm,
    UsuarioUpdateForm,
)
from .models import Usuario


class UserPermissionAssignmentTests(TestCase):
    def setUp(self):
        self.content_type = ContentType.objects.get_for_model(Usuario)
        self.permissions = {
            codename: Permission.objects.get_or_create(
                content_type=self.content_type,
                codename=codename,
                defaults={"name": name},
            )[0]
            for codename, name in {
                "add_usuario": "Can add usuario",
                "change_usuario": "Can change usuario",
                "delete_usuario": "Can delete usuario",
                "view_usuario": "Can view usuario",
                "create_questions": "Puede crear preguntas",
            }.items()
        }
        self.admin = Usuario.objects.create_user(
            username="admin",
            password="ClaveSegura-123",
        )
        self.admin.user_permissions.add(
            *(
                self.permissions[codename]
                for codename in (
                    "add_usuario",
                    "change_usuario",
                    "delete_usuario",
                    "view_usuario",
                )
            )
        )
        self.client.force_login(self.admin)

    def test_creation_form_shows_only_user_crud_permissions_as_checkboxes(self):
        form = UsuarioAdminCreationForm()

        self.assertNotIn("groups", form.fields)
        self.assertIsInstance(
            form.fields["user_permissions"].widget,
            forms.CheckboxSelectMultiple,
        )
        self.assertEqual(
            set(
                form.fields["user_permissions"].queryset.values_list(
                    "codename", flat=True
                )
            ),
            {"add_usuario", "change_usuario", "delete_usuario", "view_usuario"},
        )

        response = self.client.get(reverse("panel_usuario_crear"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ver usuarios")
        self.assertContains(response, "Crear usuarios")
        self.assertContains(response, "Actualizar usuarios")
        self.assertContains(response, "Eliminar usuarios")
        self.assertNotContains(response, "Roles")
        self.assertEqual(response.content.decode().count('type="checkbox"'), 4)

    def test_creation_saves_the_checked_permissions(self):
        selected_permissions = [
            self.permissions["add_usuario"].pk,
            self.permissions["view_usuario"].pk,
        ]
        response = self.client.post(
            reverse("panel_usuario_crear"),
            {
                "username": "nuevo",
                "email": "nuevo@example.com",
                "telefono": "",
                "user_permissions": selected_permissions,
                "password1": "ClaveSegura-123",
                "password2": "ClaveSegura-123",
            },
        )

        self.assertRedirects(response, reverse("panel_usuarios_lista"))
        user = Usuario.objects.get(username="nuevo")
        self.assertSetEqual(
            set(user.user_permissions.all()),
            {
                self.permissions["add_usuario"],
                self.permissions["view_usuario"],
            },
        )
        self.assertNotIn("groups", UsuarioAdminCreationForm().fields)

    def test_update_form_saves_selected_permissions_without_roles(self):
        target = Usuario.objects.create_user(username="usuario")
        response = self.client.post(
            reverse("panel_usuario_editar", args=[target.pk]),
            {
                "username": target.username,
                "email": "",
                "first_name": "",
                "last_name": "",
                "telefono": "",
                "is_active": "on",
                "user_permissions": [self.permissions["view_usuario"].pk],
            },
        )

        self.assertRedirects(response, reverse("panel_usuarios_lista"))
        target.refresh_from_db()
        self.assertSetEqual(
            set(target.user_permissions.all()),
            {self.permissions["view_usuario"]},
        )
        self.assertNotIn("groups", UsuarioUpdateForm().fields)

    def test_view_only_permission_does_not_allow_changes(self):
        reader = Usuario.objects.create_user(username="lector")
        reader.user_permissions.add(self.permissions["view_usuario"])
        self.client.force_login(reader)

        self.assertEqual(
            self.client.get(reverse("panel_usuarios_lista")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("panel_usuario_crear")).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                reverse("panel_usuario_editar", args=[self.admin.pk])
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                reverse("panel_usuario_eliminar", args=[self.admin.pk])
            ).status_code,
            403,
        )

    def test_create_only_user_can_open_creation_form_without_user_list(self):
        creator = Usuario.objects.create_user(username="creador")
        creator.user_permissions.add(self.permissions["add_usuario"])
        self.client.force_login(creator)

        panel_response = self.client.get(reverse("panel_inicio"))
        list_response = self.client.get(reverse("panel_usuarios_lista"))
        create_response = self.client.get(reverse("panel_usuario_crear"))
        profile_response = self.client.get(reverse("perfil_usuario"))

        self.assertRedirects(
            panel_response,
            reverse("panel_usuario_crear"),
        )
        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(create_response.status_code, 200)
        self.assertContains(profile_response, "Crear usuarios")
        self.assertContains(profile_response, "Ir al panel")
        self.assertContains(
            profile_response,
            reverse("panel_inicio"),
        )
        home_response = self.client.get(reverse("home"))
        self.assertContains(home_response, reverse("perfil_usuario"))
        self.assertContains(home_response, reverse("panel_inicio"))

        create_response = self.client.post(
            reverse("panel_usuario_crear"),
            {
                "username": "creado",
                "email": "",
                "telefono": "",
                "password1": "ClaveSegura-123",
                "password2": "ClaveSegura-123",
            },
            follow=True,
        )
        self.assertEqual(create_response.status_code, 200)
        self.assertRedirects(create_response, reverse("panel_usuario_crear"))
        self.assertContains(create_response, "Usuario creado correctamente.")
        self.assertTrue(Usuario.objects.filter(username="creado").exists())

    def test_change_only_user_cannot_assign_permissions(self):
        editor = Usuario.objects.create_user(username="editor")
        editor.user_permissions.add(self.permissions["change_usuario"])
        self.client.force_login(editor)

        list_response = self.client.get(reverse("panel_usuarios_lista"))
        response = self.client.get(
            reverse("panel_usuario_editar", args=[self.admin.pk])
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, ">Editar</a>")
        self.assertNotContains(list_response, ">Borrar</a>")
        self.assertNotContains(list_response, "+ Nuevo usuario")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="user_permissions"')

    def test_delete_only_user_sees_only_delete_action(self):
        deleter = Usuario.objects.create_user(username="eliminador")
        deleter.user_permissions.add(self.permissions["delete_usuario"])
        self.client.force_login(deleter)

        response = self.client.get(reverse("panel_usuarios_lista"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Borrar</a>")
        self.assertNotContains(response, ">Editar</a>")
        self.assertNotContains(response, "+ Nuevo usuario")

    def test_panel_shows_user_permissions_and_superadministrator_status(self):
        reader = Usuario.objects.create_user(username="lector")
        reader.user_permissions.add(self.permissions["view_usuario"])
        superadmin = Usuario.objects.create_superuser(
            username="superadmin",
            password="ClaveSegura-123",
        )

        list_response = self.client.get(reverse("panel_usuarios_lista"))
        profile_response = self.client.get(reverse("perfil_usuario"))

        self.assertContains(list_response, "Ver usuarios")
        self.assertContains(list_response, "Superadministrador · acceso completo")
        self.assertContains(profile_response, "Actualizar usuarios")
        self.assertContains(profile_response, "Eliminar usuarios")

        self.client.force_login(superadmin)
        superadmin_profile = self.client.get(reverse("perfil_usuario"))
        self.assertContains(
            superadmin_profile,
            "Superadministrador · acceso completo",
        )

    def test_regular_user_can_open_profile_from_main_navigation(self):
        user = Usuario.objects.create_user(username="alumno")
        self.client.force_login(user)

        home_response = self.client.get(reverse("home"))
        profile_response = self.client.get(reverse("perfil_usuario"))

        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, "Mi perfil")
        self.assertContains(profile_response, "alumno")
        self.assertContains(home_response, reverse("perfil_usuario"))

    def test_roles_are_not_shown_in_user_list_or_profile(self):
        list_response = self.client.get(reverse("panel_usuarios_lista"))
        profile_response = self.client.get(reverse("perfil_usuario"))

        self.assertNotContains(list_response, "Rol")
        self.assertNotContains(profile_response, "Roles")

    def test_phone_field_accepts_only_digits_in_all_user_forms(self):
        user = Usuario(username="form-user")
        user_forms = (
            RegistroPublicoForm(),
            UsuarioAdminCreationForm(),
            UsuarioUpdateForm(instance=user),
        )

        for form in user_forms:
            with self.subTest(form=form.__class__.__name__):
                phone_field = form.fields["telefono"]
                self.assertEqual(phone_field.widget.attrs["inputmode"], "numeric")
                self.assertEqual(phone_field.widget.attrs["pattern"], "[0-9]*")
                self.assertEqual(
                    phone_field.widget.attrs["data-digits-only"],
                    "true",
                )
                self.assertEqual(phone_field.clean("5551234567"), "5551234567")
                with self.assertRaises(forms.ValidationError):
                    phone_field.clean("555ABC123")

        invalid_form_data = {
            "username": "usuario-telefono-invalido",
            "email": "",
            "telefono": "555ABC123",
            "password1": "ClaveSegura-123",
            "password2": "ClaveSegura-123",
        }
        creation_forms = (
            RegistroPublicoForm(data=invalid_form_data),
            UsuarioAdminCreationForm(
                data={**invalid_form_data, "user_permissions": []}
            ),
        )
        for form in creation_forms:
            with self.subTest(form=form.__class__.__name__):
                self.assertFalse(form.is_valid())
                self.assertIn("telefono", form.errors)

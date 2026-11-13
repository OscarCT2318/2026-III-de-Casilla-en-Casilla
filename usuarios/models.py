# usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


VALIDAR_TELEFONO_NUMERICO = RegexValidator(
    regex=r"^[0-9]+$",
    message="El teléfono solo debe contener números.",
)

PERMISOS_USUARIOS = (
    ("view_usuario", "Ver usuarios"),
    ("add_usuario", "Crear usuarios"),
    ("change_usuario", "Actualizar usuarios"),
    ("delete_usuario", "Eliminar usuarios"),
)


class Usuario(AbstractUser):
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[VALIDAR_TELEFONO_NUMERICO],
    )

    ADMINISTRADOR = 'admin'
    SOLO_LECTURA = 'lectura'
    CREADOR_USUARIOS = 'creador'
    JUGADOR = 'jugador'

    ROLES_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (SOLO_LECTURA, 'Solo Lectura'),
        (CREADOR_USUARIOS, 'Creador de Usuarios'),
        (JUGADOR, 'Jugador / Alumno'),
    ]

    rol = models.CharField(
        max_length=15,
        choices=ROLES_CHOICES,
        default=JUGADOR,
    )

    class Meta:
        permissions = [
            ("create_questions", "Puede crear preguntas"),
        ]

    @property
    def puede_ver_panel(self):
        return self.is_superuser or any(
            self.has_perm(permission)
            for permission in (
                "usuarios.view_usuario",
                "usuarios.change_usuario",
                "usuarios.delete_usuario",
            )
        )

    @property
    def puede_acceder_panel(self):
        return self.puede_ver_panel or self.puede_crear_usuarios

    @property
    def permisos_usuarios_asignados(self):
        return [
            label
            for codename, label in PERMISOS_USUARIOS
            if self.has_perm(f"usuarios.{codename}")
        ]

    @property
    def puede_crear_usuarios(self):
        return self.is_superuser or self.has_perm("usuarios.add_usuario")

    @property
    def puede_editar_usuarios(self):
        return self.is_superuser or self.has_perm("usuarios.change_usuario")

    @property
    def puede_asignar_permisos_usuarios(self):
        return self.is_superuser or all(
            self.has_perm(permission)
            for permission in (
                "usuarios.view_usuario",
                "usuarios.add_usuario",
                "usuarios.change_usuario",
                "usuarios.delete_usuario",
            )
        )

    @property
    def puede_eliminar_usuarios(self):
        return self.is_superuser or self.has_perm("usuarios.delete_usuario")

    @property
    def puede_crear_preguntas(self):
        return self.has_perm("usuarios.create_questions")
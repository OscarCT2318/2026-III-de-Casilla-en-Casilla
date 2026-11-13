from django.db import migrations


ROLES = {
    "Administrador": ("add_usuario", "change_usuario", "delete_usuario", "view_usuario", "create_questions"),
    "Solo lectura": ("view_usuario",),
    "Creador de usuarios": ("add_usuario", "view_usuario"),
    "Crear preguntas": ("create_questions",),
    "Jugador": (),
}

LEGACY_ROLES = {
    "admin": "Administrador",
    "lectura": "Solo lectura",
    "creador": "Creador de usuarios",
    "jugador": "Jugador",
}

PERMISSION_NAMES = {
    "add_usuario": "Can add usuario",
    "change_usuario": "Can change usuario",
    "delete_usuario": "Can delete usuario",
    "view_usuario": "Can view usuario",
    "create_questions": "Puede crear preguntas",
}


def create_roles_and_assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Usuario = apps.get_model("usuarios", "Usuario")
    database = schema_editor.connection.alias

    content_type, _ = ContentType.objects.using(database).get_or_create(
        app_label="usuarios",
        model="usuario",
    )
    permissions = {}
    for codename, name in PERMISSION_NAMES.items():
        permissions[codename], _ = Permission.objects.using(database).get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={"name": name},
        )

    groups = {}
    for role_name, codenames in ROLES.items():
        group, _ = Group.objects.using(database).get_or_create(name=role_name)
        group.permissions.add(*(permissions[codename] for codename in codenames))
        groups[role_name] = group

    for user in Usuario.objects.using(database).all().iterator():
        role_name = LEGACY_ROLES.get(user.rol, "Jugador")
        user.groups.add(groups[role_name])


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0002_alter_usuario_rol"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="usuario",
            options={
                "permissions": [("create_questions", "Puede crear preguntas")],
            },
        ),
        migrations.RunPython(create_roles_and_assign_permissions, migrations.RunPython.noop),
    ]

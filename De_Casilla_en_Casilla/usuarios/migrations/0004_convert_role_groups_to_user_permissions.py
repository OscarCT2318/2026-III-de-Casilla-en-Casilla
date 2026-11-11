from django.db import migrations


ROLE_GROUP_NAMES = (
    "Administrador",
    "Solo lectura",
    "Creador de usuarios",
    "Crear preguntas",
    "Jugador",
)


def convert_role_groups_to_user_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Usuario = apps.get_model("usuarios", "Usuario")
    database = schema_editor.connection.alias

    for group in Group.objects.using(database).filter(name__in=ROLE_GROUP_NAMES):
        permissions = list(group.permissions.using(database).all())
        users = Usuario.objects.using(database).filter(
            groups__pk=group.pk
        ).distinct()
        for user in users.iterator():
            user.user_permissions.add(*permissions)
            user.groups.remove(group)
        group.delete(using=database)


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0003_assignable_roles_and_question_permission"),
    ]

    operations = [
        migrations.RunPython(
            convert_role_groups_to_user_permissions,
            migrations.RunPython.noop,
        ),
    ]

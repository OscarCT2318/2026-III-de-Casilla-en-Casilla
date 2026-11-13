from django.db import migrations

def crear_niveles(apps, schema_editor):
    Nivel = apps.get_model('preguntas', 'Nivel')
    Nivel.objects.get_or_create(nombre='Nivel Alfa', tipo='ALFA', defaults={'descripcion': 'Nivel educativo Alfa'})
    Nivel.objects.get_or_create(nombre='Nivel Beta', tipo='BETA', defaults={'descripcion': 'Nivel educativo Beta'})

class Migration(migrations.Migration):

    dependencies = [
        ('preguntas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_niveles),
    ]
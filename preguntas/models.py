from django.db import models
from django.conf import settings

class Nivel(models.Model):
    TIPO_NIVEL_CHOICES = [
        ('ALFA', 'Alfa'),
        ('BETA', 'Beta'),
    ]
    
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=TIPO_NIVEL_CHOICES, default='ALFA')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Pregunta(models.Model):
    enunciado = models.TextField()
    opcion_a = models.CharField(max_length=255)
    opcion_b = models.CharField(max_length=255)
    opcion_c = models.CharField(max_length=255)
    opcion_d = models.CharField(max_length=255)
    
    RESPUESTAS_CHOICES = [
        ('A', 'Opción A'),
        ('B', 'Opción B'),
        ('C', 'Opción C'),
        ('D', 'Opción D'),
    ]
    respuesta_correcta = models.CharField(max_length=1, choices=RESPUESTAS_CHOICES)
    
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='preguntas')
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='preguntas_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.nivel.nombre}] {self.enunciado[:50]}"
from django import forms
from .models import Pregunta

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = [
            'nivel',
            'enunciado',
            'opcion_a',
            'opcion_b',
            'opcion_c',
            'opcion_d',
            'respuesta_correcta',
        ]
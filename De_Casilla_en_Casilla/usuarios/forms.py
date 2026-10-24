from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from .models import Usuario


class UsuarioCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'rol', 'telefono')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            )
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre'
        self.fields['username'].help_text = ''
        self.fields['email'].widget.attrs['placeholder'] = 'Correo'
        self.fields['telefono'].widget.attrs['placeholder'] = 'Teléfono'
        self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar contraseña'

class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'rol', 'telefono')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'content_type']
        labels = {
            'name': 'Nombre del Permiso',
            'codename': 'Código (Codename)',
            'content_type': 'Módulo Asociado',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'codename': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content_type'].queryset = ContentType.objects.all()

        traducciones = {
            'user': 'Módulo de Usuario',
            'usuario': 'Módulo de Usuarios',
            'permission': 'Módulo de Permisos',
            'group': 'Módulo de Grupos',
            'session': 'Módulo de Sesiones',
            'logentry': 'Módulo de Administración',
            'contenttype': 'Tipos de Contenido',
        }

        self.fields['content_type'].label_from_instance = lambda obj: traducciones.get(
            obj.model.lower(),
            f"Módulo de {obj.model.capitalize()}"
        )

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission


from .models import (
    PERMISOS_USUARIOS,
    VALIDAR_TELEFONO_NUMERICO,
    Usuario,
)


def configurar_campo_telefono(form):
    field = form.fields['telefono']
    field.validators.append(VALIDAR_TELEFONO_NUMERICO)
    field.widget.attrs.update(
        {
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'maxlength': '20',
            'title': 'Ingresa solo números.',
            'data-digits-only': 'true',
        }
    )


def aplicar_estilos_bootstrap(form):
    """Aplica las clases de Bootstrap a todos los campos del formulario automáticamente"""
    for field in form.fields.values():
        if isinstance(field.widget, forms.Select):
            field.widget.attrs['class'] = 'form-select'
        elif isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs['class'] = 'form-check-input'
        else:
            field.widget.attrs['class'] = 'form-control'

class RegistroPublicoForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'telefono')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['username'].help_text = ''
        self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
        self.fields['telefono'].widget.attrs['placeholder'] = 'Teléfono'
        self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar contraseña'
        configurar_campo_telefono(self)


def configurar_permisos_usuario(form):
    field = form.fields['user_permissions']
    field.queryset = Permission.objects.filter(
        content_type__app_label='usuarios',
        content_type__model='usuario',
        codename__in=[codename for codename, _ in PERMISOS_USUARIOS],
    ).order_by('codename')
    field.label = 'Permisos de usuarios'
    field.help_text = 'Marca las acciones que este usuario puede realizar.'
    permission_labels = dict(PERMISOS_USUARIOS)
    field.label_from_instance = lambda permission: permission_labels[
        permission.codename
    ]
    field.widget = forms.CheckboxSelectMultiple(
        attrs={'class': 'permission-checkbox'},
    )
    field.widget.choices = field.choices


class UsuarioAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'telefono', 'user_permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)
        self.fields['username'].help_text = ''
        configurar_campo_telefono(self)
        configurar_permisos_usuario(self)


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario

        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'telefono',
            'is_active',
            'user_permissions',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)
        configurar_campo_telefono(self)
        configurar_permisos_usuario(self)
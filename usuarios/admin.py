from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Modelos personalizados de Usuario y Permiso
admin.site.register(Usuario, UserAdmin)
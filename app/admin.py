from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Curso, Carrito, Inscripcion, Unidad, Pregunta, Opcion


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "role", "is_staff"]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Curso)
admin.site.register(Inscripcion)
admin.site.register(Carrito)
admin.site.register(Unidad)
admin.site.register(Pregunta)
admin.site.register(Opcion)
# Register your models here.

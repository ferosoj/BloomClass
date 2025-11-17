from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Curso, Carrito, Inscripcion, Unidad, Pregunta, Opcion, Pago, ItemTienda, Inventario



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
admin.site.register (Pago)
# Register your models here.

@admin.register(ItemTienda)
class ItemTiendaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio", "miniatura") 
    list_filter = ("tipo",)
    search_fields = ("nombre",)
    readonly_fields = ("miniatura",)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "item", "equipado")
    list_filter = ("equipado", "item__tipo")
    search_fields = ("usuario__username", "item__nombre")
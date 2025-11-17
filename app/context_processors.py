from .models import Inventario

def icono_equipado(request):
    usuario = request.user
    if usuario.is_authenticated:
        inv = Inventario.objects.filter(usuario=usuario, equipado=True).first()
        if inv and inv.item.archivo:
            return {'icono_equipado': inv.item.archivo.url}
    return {'icono_equipado': None}
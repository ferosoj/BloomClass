from django import template

register = template.Library()

@register.filter
def get_item(dictionary_or_list, key):
    """
    Intenta obtener un elemento usando .get() (para diccionarios) o 
    verifica la existencia del elemento (para listas/iterables).
    
    Uso en plantilla: {{ unidad.id|get_item:unidades_completadas_ids }}
    """
    if hasattr(dictionary_or_list, 'get'):
        # Si es un diccionario, usa .get()
        return dictionary_or_list.get(key)
    elif isinstance(dictionary_or_list, (list, tuple)):
        # Si es una lista o tupla, verifica si la clave está contenida
        # Retorna la clave si la encuentra, o None si no
        return key if key in dictionary_or_list else None
    else:
        # Retorna None si el objeto no es ni diccionario ni lista
        return None

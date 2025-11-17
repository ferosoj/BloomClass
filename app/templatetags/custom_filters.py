from django import template

register = template.Library()

@register.filter
def get_item(dictionary_or_list, key):
    if hasattr(dictionary_or_list, 'get'):
        return dictionary_or_list.get(key)
    elif isinstance(dictionary_or_list, (list, tuple)):
        return key if key in dictionary_or_list else None
    return None

@register.filter
def dict_get(d, key):
    if d is None:
        return None
    return d.get(key)

@register.filter
def in_list(value, lista):
    return value in lista

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item(dictionary, key):
    """Permite acceder a valores de un diccionario desde el template."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
from django import template
from facultad.models import Alerta

register = template.Library()

@register.simple_tag
def get_alertas():
    # Traemos las alertas que tengan el tilde de "mostrar" activado
    return Alerta.objects.filter(mostrar=True)
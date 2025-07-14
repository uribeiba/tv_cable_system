from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Agrega una clase CSS al widget del campo de formulario.
    Si el campo no tiene el método 'as_widget', se retorna el campo original.
    """
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        # Devuelve el campo original si no es un objeto de formulario válido
        return field

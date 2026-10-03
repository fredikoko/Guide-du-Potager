from django import template
from django.utils.safestring import mark_safe
from apps.content.rendering import render_content as parse_content

register = template.Library()

@register.filter(name='render_content', is_safe=True)
def render_content_filter(value):
    """
    Filtre de template Django pour convertir du Markdown, HTML ou texte brut
    en HTML riche sécurisé pour l'affichage web.
    Usage : {{ post.content|render_content }} ou {{ chapter.content|render_content }}
    """
    if not value:
        return ""
    rendered = parse_content(value)
    return mark_safe(rendered)

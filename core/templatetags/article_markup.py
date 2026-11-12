from django import template

from core.markup import render_article

register = template.Library()


@register.filter
def article_markup(value):
    return render_article(value)

from django import template

register = template.Library()

@register.filter()
def get(dictionary, key):
    return dictionary.get(key, '')

@register.filter()
def get_title(dictionary, entity):
    # Has performance impact, more efficient solution
    # would be better.
    bwb = entity.split('/')[0]
    return dictionary.get(bwb, '')
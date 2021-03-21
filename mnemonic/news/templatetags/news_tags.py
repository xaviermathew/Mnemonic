from django.template.defaulttags import register


@register.simple_tag
def lookup(dictionary, key, default=None):
    return dictionary.get(key, default)

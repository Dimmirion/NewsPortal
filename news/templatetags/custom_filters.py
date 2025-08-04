# news/templatetags/custom_filters.py
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter()
@stringfilter  # Гарантирует, что фильтр применяется только к строкам
def censor(value):
    unwanted_words = ['редиска', 'негодяй', 'подлец']  # Список нежелательных слов

    if not isinstance(value, str):
        raise ValueError("Фильтр 'censor' можно применять только к строкам")

    for word in unwanted_words:
        # Заменяем слово независимо от регистра первой буквы
        value = value.replace(word, word[0] + '*' * (len(word) - 1))
        value = value.replace(word.capitalize(), word[0].upper() + '*' * (len(word) - 1))

    return value
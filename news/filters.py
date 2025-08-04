import django_filters
from .models import Post
from django import forms

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    author__user__username = django_filters.CharFilter(lookup_expr='icontains', label='Автор')
    date_created = django_filters.DateFilter(
        lookup_expr='gt',  # "позже указанной даты"
        label='Дата (позже)',
        widget=forms.DateInput(attrs={'type': 'date'})  # Календарь HTML5
    )

    class Meta:
        model = Post
        fields = []
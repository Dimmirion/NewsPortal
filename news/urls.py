from django.urls import path
from .views import (
    NewsList, NewsSearch, NewsCreate, ArticleCreate,
    PostUpdateView, PostDelete,  # Изменено PostUpdate на PostUpdateView
    become_author, subscribe, unsubscribe
)

app_name = 'news'

urlpatterns = [
    path('news/', NewsList.as_view(), name='news_list'),
    path('news/search/', NewsSearch.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    # Изменено PostUpdate на PostUpdateView в следующих двух строках
    path('news/<int:pk>/edit/', PostUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', PostUpdateView.as_view(), name='article_edit'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('become-author/', become_author, name='become_author'),
    path('category/<int:category_id>/subscribe/', subscribe, name='subscribe'),
    path('category/<int:category_id>/unsubscribe/', unsubscribe, name='unsubscribe'),
]
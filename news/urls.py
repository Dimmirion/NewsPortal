from django.urls import path
from .views import (
    NewsList, NewsSearch, NewsCreate, ArticleCreate,
    PostUpdateView, PostDelete,
    become_author, subscribe, unsubscribe,
    PostListAPI, PostDetailAPI, NewsListAPI, NewsDetailAPI, ArticleListAPI, ArticleDetailAPI
)

app_name = 'news'

urlpatterns = [
    # Стандартные Django маршруты (для HTML-шаблонов)
    path('news/', NewsList.as_view(), name='news_list'),
    path('news/search/', NewsSearch.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('news/<int:pk>/edit/', PostUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', PostUpdateView.as_view(), name='article_edit'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('become-author/', become_author, name='become_author'),
    path('category/<int:category_id>/subscribe/', subscribe, name='subscribe'),
    path('category/<int:category_id>/unsubscribe/', unsubscribe, name='unsubscribe'),

    # REST API маршруты
    path('api/posts/', PostListAPI.as_view(), name='api-post-list'),
    path('api/posts/<int:pk>/', PostDetailAPI.as_view(), name='api-post-detail'),
    path('api/news/', NewsListAPI.as_view(), name='api-news-list'),
    path('api/news/<int:pk>/', NewsDetailAPI.as_view(), name='api-news-detail'),
    path('api/articles/', ArticleListAPI.as_view(), name='api-article-list'),
    path('api/articles/<int:pk>/', ArticleDetailAPI.as_view(), name='api-article-detail'),
]
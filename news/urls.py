from django.urls import path
from .views import NewsList, NewsSearch, NewsCreate, ArticleCreate, PostUpdate, PostDelete
from .views import PostUpdateView
from .views import become_author  # Импортируем функцию
from .views import subscribe, unsubscribe

app_name = 'news'

urlpatterns = [
    path('news/', NewsList.as_view(), name='news_list'),
    path('news/', NewsList.as_view(), name='news_list'),          # Список новостей
    path('news/search/', NewsSearch.as_view(), name='news_search'),  # Поиск
    path('news/create/', NewsCreate.as_view(), name='news_create'),  # Создание новости
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),  # Создание статьи
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_edit'),      # Редактирование
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='article_edit'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),  # Удаление
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('become-author/', become_author, name='become_author'),
    path('category/<int:category_id>/subscribe/', subscribe, name='subscribe'),
    path('category/<int:category_id>/unsubscribe/', unsubscribe, name='unsubscribe'),
]
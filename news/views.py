from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from django.core.paginator import Paginator

from .models import Post
from .filters import PostFilter

# Список новостей с пагинацией
class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'news'
    ordering = ['-date_created']
    paginate_by = 10  # 10 новостей на страницу

# Поиск новостей
class NewsSearch(ListView):
    model = Post
    template_name = 'news/news_search.html'
    ordering = ['-date_created']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

# Создание новости
class NewsCreate(CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'news/news_create.html'

    def form_valid(self, form):
        form.instance.post_type = Post.NEWS  # Автоматически ставим тип "Новость"
        return super().form_valid(form)

# Создание статьи
class ArticleCreate(CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'news/article_create.html'

    def form_valid(self, form):
        form.instance.post_type = Post.ARTICLE  # Автоматически ставим тип "Статья"
        return super().form_valid(form)

# Редактирование (общее для новостей и статей)
class PostUpdate(UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'news/post_edit.html'

# Удаление (общее для новостей и статей)
class PostDelete(DeleteView):
    model = Post
    template_name = 'news/post_delete.html'
    success_url = '/news/'


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from .models import Post

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content']  # Укажите нужные поля
    template_name = 'post_edit.html'  # Шаблон для редактирования
    success_url = '/'  # Куда перенаправлять после успешного редактирования

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from django.shortcuts import redirect

@login_required
def become_author(request):
    author_group = Group.objects.get(name='authors')
    request.user.groups.add(author_group)
    return redirect('/')

from django.contrib.auth.mixins import PermissionRequiredMixin

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    ...

class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    ...

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Category, Subscriber

@login_required
def subscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subscriber, created = Subscriber.objects.get_or_create(user=request.user)
    subscriber.categories.add(category)
    return redirect('category_detail', category_id=category.id)

@login_required
def unsubscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subscriber = get_object_or_404(Subscriber, user=request.user)
    subscriber.categories.remove(category)
    return redirect('category_detail', category_id=category.id)


from django.views.decorators.cache import cache_page
from django.core.cache import cache


def get_sidebar_data():
    """Функция для получения данных сайдбара с кэшированием"""
    cache_key = 'sidebar_data'
    data = cache.get(cache_key)

    if not data:
        categories = Category.objects.all()
        popular_news = News.objects.order_by('-views')[:5]
        data = {
            'categories': categories,
            'popular_news': popular_news,
        }
        cache.set(cache_key, data, 300)  # Кэшируем на 5 минут

    return data

from django.views.decorators.cache import cache_page
from django.core.cache import cache


@cache_page(60)  # Кэшируем главную страницу на 1 минуту
def home(request):
    categories = Category.objects.all()
    popular_news = News.objects.order_by('-views')[:5]
    context = {
        'title': 'Главная страница',
        'categories': categories,
        'popular_news': popular_news,
    }
    return render(request, 'news/home.html', context)


def news_list(request):
    news = News.objects.all()
    context = {
        'title': 'Все новости',
        'news': news,
    }
    return render(request, 'news/news_list.html', context)


def news_detail(request, pk):
    # Кэширование отдельной статьи
    cache_key = f'news_detail_{pk}'
    news = cache.get(cache_key)

    if not news:
        news = get_object_or_404(News, pk=pk)
        # Увеличиваем счетчик просмотров
        news.views += 1
        news.save()
        # Кэшируем на 5 минут или пока статья не изменится
        cache.set(cache_key, news, 300)

    context = {
        'title': news.title,
        'news': news,
    }
    return render(request, 'news/news_detail.html', context)
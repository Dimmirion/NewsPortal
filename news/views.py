from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.contrib.auth.models import Group

from rest_framework import generics, permissions
from .models import Post, Category, Subscriber
from .filters import PostFilter
from .forms import TimeZoneForm
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly


# Стандартные Django представления
class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'news'
    ordering = ['-date_created']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['active_category'] = self.request.GET.get('category')
        return context


class NewsSearch(ListView):
    model = Post
    template_name = 'news/news_search.html'
    ordering = ['-date_created']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        context['active_category'] = self.request.GET.get('category')
        return context


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'news/news_create.html'

    def form_valid(self, form):
        form.instance.post_type = Post.NEWS
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'news/article_create.html'

    def form_valid(self, form):
        form.instance.post_type = Post.ARTICLE
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'news/post_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/post_delete.html'
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# REST API представления
class PostListAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        post_type = self.request.query_params.get('type', None)

        if post_type == 'news':
            return queryset.filter(post_type=Post.NEWS)
        elif post_type == 'article':
            return queryset.filter(post_type=Post.ARTICLE)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class NewsListAPI(generics.ListCreateAPIView):
    queryset = Post.objects.filter(post_type=Post.NEWS)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_type=Post.NEWS)


class NewsDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(post_type=Post.NEWS)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class ArticleListAPI(generics.ListCreateAPIView):
    queryset = Post.objects.filter(post_type=Post.ARTICLE)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_type=Post.ARTICLE)


class ArticleDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(post_type=Post.ARTICLE)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


# Функциональные представления
@login_required
def become_author(request):
    author_group = Group.objects.get_or_create(name='authors')[0]
    request.user.groups.add(author_group)
    return redirect('/')


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


@cache_page(60)
def home(request):
    news_items = Post.objects.order_by('-date_created')[:5]
    paginator = Paginator(news_items, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'news': news_items,
        'categories': Category.objects.all(),
        'active_category': request.GET.get('category'),
        'is_paginated': True,
        'page_obj': page_obj,
        'popular_news': Post.objects.order_by('-views')[:5],
    }
    return render(request, 'news/index.html', context)


def news_list(request):
    category = request.GET.get('category')
    if category:
        news_items = Post.objects.filter(category__slug=category).order_by('-date_created')
    else:
        news_items = Post.objects.order_by('-date_created')

    paginator = Paginator(news_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'news': news_items,
        'categories': Category.objects.all(),
        'active_category': category,
        'is_paginated': True,
        'page_obj': page_obj,
    }
    return render(request, 'news/news_list.html', context)


def news_detail(request, pk):
    cache_key = f'news_detail_{pk}'
    news = cache.get(cache_key)

    if not news:
        news = get_object_or_404(Post, pk=pk)
        news.views += 1
        news.save()
        cache.set(cache_key, news, 300)

    context = {
        'news': news,
        'categories': Category.objects.all(),
        'related_news': Post.objects.filter(category=news.category).exclude(pk=pk)[:3],
    }
    return render(request, 'news/news_detail.html', context)


def set_timezone(request):
    if request.method == 'POST':
        form = TimeZoneForm(request.POST)
        if form.is_valid():
            request.session['django_timezone'] = form.cleaned_data['timezone']
            return redirect('home')
    else:
        form = TimeZoneForm()

    context = {
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'timezone_form.html', context)


def get_sidebar_data():
    cache_key = 'sidebar_data'
    data = cache.get(cache_key)

    if not data:
        categories = Category.objects.all()
        popular_news = Post.objects.order_by('-views')[:5]
        data = {
            'categories': categories,
            'popular_news': popular_news,
        }
        cache.set(cache_key, data, 300)

    return data
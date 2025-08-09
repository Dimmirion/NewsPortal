from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Author, Category, Post, PostCategory, Comment, Subscriber


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'rating', 'posts_count')
    list_filter = ('rating',)
    search_fields = ('user__username', 'user__email')

    def user_info(self, obj):
        return f"{obj.user.username} ({obj.user.email})"

    user_info.short_description = 'Пользователь'

    def posts_count(self, obj):
        return obj.post_set.count()

    posts_count.short_description = 'Кол-во постов'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'posts_count', 'subscribers_count')
    list_filter = ('post__post_type',)
    search_fields = ('name',)

    def colored_name(self, obj):
        color = 'FF0000' if obj.post_set.count() > 5 else '00AA00'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            obj.name
        )

    colored_name.short_description = 'Название'

    def posts_count(self, obj):
        return obj.post_set.count()

    posts_count.short_description = 'Постов'

    def subscribers_count(self, obj):
        return obj.subscribers.count()

    subscribers_count.short_description = 'Подписчиков'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _posts_count=Count('post'),
            _subscribers_count=Count('subscribers')
        )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'created_at', 'rating')
    list_filter = ('post_type', 'created_at', 'categories')
    search_fields = ('title', 'text')
    # Убрали filter_horizontal для categories

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'post_link', 'user', 'created_at', 'rating', 'is_active')
    list_filter = ('is_active', 'created_at', 'rating')
    search_fields = ('text', 'user__username', 'post__title')
    list_editable = ('is_active',)
    actions = ['approve_comments', 'disapprove_comments']

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = 'Текст'

    def post_link(self, obj):
        return format_html(
            '<a href="/admin/news/post/{}/">{}</a>',
            obj.post.id,
            obj.post.title[:30] + '...' if len(obj.post.title) > 30 else obj.post.title
        )

    post_link.short_description = 'Пост'

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)

    approve_comments.short_description = "Одобрить выбранные комментарии"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_active=False)

    disapprove_comments.short_description = "Запретить выбранные комментарии"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('post', 'user')


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('post_info', 'category_info')
    list_filter = ('category', 'post__post_type')
    search_fields = ('post__title', 'category__name')

    def post_info(self, obj):
        return f"{obj.post.title} ({obj.post.get_post_type_display()})"

    post_info.short_description = 'Пост'

    def category_info(self, obj):
        return obj.category.name

    category_info.short_description = 'Категория'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('post', 'category')

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'email_verified')
    list_filter = ('email_verified', 'category')
    search_fields = ('user__username', 'category__name')
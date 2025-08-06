from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.html import format_html
from django.urls import reverse
from django.core.validators import MinLengthValidator


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    def update_rating(self):
        post_ratings = self.post_set.aggregate(post_rating=Sum('rating'))
        post_r = post_ratings.get('post_rating') or 0

        comment_ratings = self.user.comment_set.aggregate(comment_rating=Sum('rating'))
        comment_r = comment_ratings.get('comment_rating') or 0

        post_comments_ratings = Comment.objects.filter(post__author=self).aggregate(comments_rating=Sum('rating'))
        p_comment_r = post_comments_ratings.get('comments_rating') or 0

        self.rating = post_r * 3 + comment_r + p_comment_r
        self.save()

    def __str__(self):
        return f'{self.user.username} (Рейтинг: {self.rating})'

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    post_type = models.CharField(
        max_length=2,
        choices=POST_TYPES,
        default=NEWS,
        verbose_name='Тип поста'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    categories = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категории')
    title = models.CharField(max_length=200, validators=[MinLengthValidator(10)], verbose_name='Заголовок')
    text = models.TextField(validators=[MinLengthValidator(50)], verbose_name='Текст')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

    def short_content(self):
        return self.text[:100] + '...' if len(self.text) > 100 else self.text
    short_content.short_description = 'Краткое содержание'

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def category_list(self):
        return ", ".join([c.name for c in self.categories.all()])
    category_list.short_description = 'Категории'

    def __str__(self):
        return f'{self.title} ({self.get_post_type_display()})'

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['rating']),
        ]


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post.title} -> {self.category.name}'

    class Meta:
        verbose_name = 'Категория поста'
        verbose_name_plural = 'Категории постов'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Пост')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def short_text(self):
        return self.text[:50] + '...' if len(self.text) > 50 else self.text
    short_text.short_description = 'Текст'

    def __str__(self):
        return f'Комментарий {self.user.username} к "{self.post.title}"'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']


class Subscriber(models.Model):
    user = models.ForeignKey(  # Изменили OneToOne на ForeignKey
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    category = models.ForeignKey(  # Изменили ManyToMany на ForeignKey
        Category,
        on_delete=models.CASCADE,
        related_name='category_subscribers'
    )
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category')  # Один пользователь - одна подписка на категорию
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user.username} -> {self.category.name}'
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Calculate post ratings
        post_ratings = self.post_set.aggregate(post_rating=Sum('rating'))
        post_r = post_ratings.get('post_rating') or 0

        # Calculate comment ratings
        comment_ratings = self.user.comment_set.aggregate(comment_rating=Sum('rating'))
        comment_r = comment_ratings.get('comment_rating') or 0

        # Calculate comments to author's posts
        post_comments_ratings = Comment.objects.filter(post__author=self).aggregate(comments_rating=Sum('rating'))
        p_comment_r = post_comments_ratings.get('comments_rating') or 0

        # Update total rating
        self.rating = post_r * 3 + comment_r + p_comment_r
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]
    post_type = models.CharField(max_length=2, choices=POST_TYPES)


    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=10, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

# news/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User

@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    if created:
        common_group = Group.objects.get_or_create(name='common')[0]
        instance.groups.add(common_group)


from django.db import models
from django.contrib.auth.models import User

class Subscriber(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    categories = models.ManyToManyField(
        'Category',
        related_name='subscribers'
    )
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user.username} (подписан на {self.categories.count()} категорий)'
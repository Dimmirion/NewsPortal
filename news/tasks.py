from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Post, Category, Subscriber


@shared_task(bind=True)
def send_notifications(self, post_id):
    try:
        post = Post.objects.get(id=post_id)
        categories = post.categories.all()

        for category in categories:
            subscribers = Subscriber.objects.filter(categories=category)
            for subscriber in subscribers:
                send_mail(
                    subject=f'Новая статья в категории {category.name}',
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.user.email],
                    html_message=render_to_string(
                        'news/post_created_email.html',
                        {'post': post, 'category': category}
                    )
                )
        return "Уведомления отправлены"
    except Exception as e:
        self.retry(exc=e, countdown=60)


@shared_task
def weekly_newsletter():
    # Рассчитываем дату "неделю назад"
    last_week = timezone.now() - timedelta(days=7)

    # Получаем все посты за последнюю неделю
    posts = Post.objects.filter(created_at__gte=last_week)

    # Если нет новых постов - выходим
    if not posts.exists():
        return

    # Получаем все категории
    categories = Category.objects.all()

    for category in categories:
        # Находим всех подписчиков этой категории через ManyToMany
        subscribers = Subscriber.objects.filter(categories=category).select_related('user')

        # Если нет подписчиков - пропускаем категорию
        if not subscribers.exists():
            continue

        # Фильтруем посты по текущей категории
        posts_in_category = posts.filter(categories=category)

        # Если нет постов в категории - пропускаем
        if not posts_in_category.exists():
            continue

        # Формируем список email подписчиков
        subscribers_emails = [subscriber.user.email for subscriber in subscribers if subscriber.user.email]

        # Подготавливаем тему письма
        subject = f'Еженедельная подборка новостей в категории {category.name}'

        # Рендерим HTML содержимое письма
        html_content = render_to_string(
            'news/weekly_newsletter.html',
            {
                'posts': posts_in_category,
                'category': category,
            }
        )

        # Отправляем письмо всем подписчикам
        send_mail(
            subject=subject,
            message='',  # Текстовая версия (пустая, т.к. используем html)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=subscribers_emails,
            html_message=html_content,
        )

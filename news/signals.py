from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        subscribers = Subscriber.objects.filter(category__in=instance.category.all())
        for subscriber in subscribers:
            subject = f'Новая статья в категории {instance.category.name}'
            message = f'Здравствуйте, {subscriber.user.username}!\n\n'
            message += f'Новая статья: {instance.title}\n'
            message += f'Краткое содержание: {instance.text[:50]}...\n\n'

            post_url = request.build_absolute_uri(
                reverse('post_detail', args=[instance.id])
            )

            message += f'Читать полностью: {post_url}'

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.user.email],
                fail_silently=False
            )


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Добро пожаловать в NewsPortal!'
        message = f'Здравствуйте, {instance.username}!\n\n'
        message += 'Спасибо за регистрацию на нашем новостном портале.\n'
        message += 'Теперь вы можете подписываться на интересные категории и получать уведомления о новых статьях.\n\n'
        message += 'Приятного пользования!'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False
        )
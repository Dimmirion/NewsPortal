# management/commands/weekly_digest.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string

from news.models import Post
from accounts.models import Subscriber


class Command(BaseCommand):
    help = 'Send weekly digest to subscribers'

    def handle(self, *args, **options):
        week_ago = timezone.now() - timezone.timedelta(days=7)

        for subscriber in Subscriber.objects.all():
            new_posts = Post.objects.filter(
                category=subscriber.category,
                created_at__gte=week_ago
            )

            if new_posts.exists():
                subject = f'Еженедельный дайджест: {subscriber.category.name}'

                context = {
                    'user': subscriber.user,
                    'category': subscriber.category,
                    'posts': new_posts,
                    'site_url': settings.SITE_URL
                }

                message = render_to_string('emails/weekly_digest.txt', context)
                html_message = render_to_string('emails/weekly_digest.html', context)

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.user.email],
                    html_message=html_message,
                    fail_silently=False
                )


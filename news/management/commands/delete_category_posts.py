from django.core.management.base import BaseCommand
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаляет все новости из указанной категории'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        category_name = options['category']

        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Категория "{category_name}" не найдена'))
            return

        count = Post.objects.filter(category=category).count()

        if count == 0:
            self.stdout.write(self.style.WARNING(f'В категории "{category_name}" нет новостей'))
            return

        self.stdout.write(self.style.WARNING(
            f'Вы собираетесь удалить {count} новостей из категории "{category_name}"'))
        confirm = input('Вы уверены? [y/N]: ')

        if confirm.lower() == 'y':
            Post.objects.filter(category=category).delete()
            self.stdout.write(self.style.SUCCESS(
                f'Успешно удалено {count} новостей из категории "{category_name}"'))
        else:
            self.stdout.write('Отменено')
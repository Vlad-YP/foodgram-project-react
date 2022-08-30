import csv
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Загрузка ингридиентов в БД'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='tags.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                      encoding='utf-8') as f:
                data = csv.reader(f)
                for row in data:
                    name, color, slug = row
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug
                    )
        except Exception as error:
            logger.error(error)

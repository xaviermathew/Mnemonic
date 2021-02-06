from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from mnemonic.news.utils.cache_utils import DiskCacheManager


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--since-hours', default=None, type=int,
                            help="How many hours of data to update")

    def handle(self, *args, **options):
        if options['since_hours']:
            since = datetime.today() - timedelta(hours=options['since_hours'])
        else:
            since = None
        for name, cfg in settings.DISK_CACHES.items():
            DiskCacheManager.update(name, since=since)

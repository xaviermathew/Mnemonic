from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from mnemonic.entity.models import Person


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--since-hours', default=None, type=int,
                            help="How many hours of tweets to crawl")

    def handle(self, *args, **options):
        if options['since_hours']:
            since = datetime.today() - timedelta(hours=options['since_hours'])
        else:
            since = None
        for person in Person.objects.all():
            person.crawl_tweets_async(since=since)

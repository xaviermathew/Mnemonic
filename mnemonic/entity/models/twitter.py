import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from mnemonic.entity.models.base import EntityBase

_LOG = logging.getLogger(__name__)


class TwitterMixin(EntityBase):
    twitter_handle = models.CharField(max_length=256, unique=True)

    class Meta:
        abstract = True

    def _crawl_tweets(self, limit=None, since=None, until=None, mentions=False, only_cached=False):
        from mnemonic.news.models import TwitterJob
        from mnemonic.news.utils.twitter_utils import CrawlBuffer

        cb = CrawlBuffer(self.twitter_handle,
                         limit=limit,
                         since=since,
                         until=until,
                         mentions=mentions,
                         language='en' if mentions else None,
                         only_cached=only_cached)
        tj, _ = TwitterJob.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            filters=cb.filters
        )
        if tj.is_crawled:
            _LOG.info('%s is already crawled', tj)
        else:
            _LOG.info('starting twitter crawl for %s', tj)
            cb.start_crawl()
            tj.is_crawled = True
            tj.save(update_fields=['is_crawled'])

    def crawl_tweets(self, limit=None, since=None, until=None, mentions=None, only_cached=False):
        if self.twitter_handle is None:
            _LOG.warning('%s does not have a twitter handle', self)
            return

        if mentions is None:
            mentions = [False, True]
        for mentions in mentions:
            self._crawl_tweets(limit=limit, since=since, until=until, mentions=mentions, only_cached=only_cached)

    def crawl_tweets_async(self, limit=None, since=None, until=None, mentions=None):
        from mnemonic.entity.tasks import crawl_tweets_async
        crawl_tweets_async.apply_async(kwargs={'entity_ct': ContentType.objects.get_for_model(self).pk,
                                               'entity_id': self.pk,
                                               'limit': limit,
                                               'since': since,
                                               'until': until,
                                               'mentions': mentions},
                                       queue=settings.CELERY_TASK_QUEUE_CRAWL_TWITTER,
                                       routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_TWITTER)

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

    def _crawl_tweets(self, since=None, until=None, mentions=False, only_cached=False):
        from mnemonic.news.models import TwitterJob
        TwitterJob.create(self, since=since, until=until, mentions=mentions, only_cached=only_cached)

    def crawl_tweets(self, since=None, until=None, mentions=None, only_cached=False):
        if self.twitter_handle is None:
            _LOG.warning('%s does not have a twitter handle', self)
            return

        if mentions is None:
            mentions = [False, True]
        for mentions in mentions:
            self._crawl_tweets(since=since, until=until, mentions=mentions, only_cached=only_cached)

    def crawl_tweets_async(self, since=None, until=None, mentions=None):
        from mnemonic.entity.tasks import crawl_tweets_async
        crawl_tweets_async.apply_async(kwargs={'entity_ct': ContentType.objects.get_for_model(self).pk,
                                               'entity_id': self.pk,
                                               'since': since,
                                               'until': until,
                                               'mentions': mentions},
                                       queue=settings.CELERY_TASK_QUEUE_CRAWL_TWITTER,
                                       routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_TWITTER)

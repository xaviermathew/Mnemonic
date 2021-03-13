from django.contrib.contenttypes.models import ContentType

from mnemonic.core.celery import app as celery_app


@celery_app.task(ignore_result=True)
def crawl_tweets_async(entity_ct, entity_id, since, until, mentions):
    klass = ContentType.objects.get_for_id(entity_ct).model_class()
    entity = klass.objects.get(pk=entity_id)
    entity.crawl_tweets(since=since, until=until, mentions=mentions)

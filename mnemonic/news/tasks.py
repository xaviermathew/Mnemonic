from mnemonic.core.celery import app as celery_app


@celery_app.task(ignore_result=True)
def crawl_feed_async(feed_id):
    from mnemonic.news.models import Feed

    feed = Feed.objects.get(pk=feed_id)
    feed.crawl_feed()


@celery_app.task(ignore_result=True)
def process_article_async(article_id):
    from mnemonic.news.models import Article

    article = Article.objects.get(pk=article_id)
    article.process()

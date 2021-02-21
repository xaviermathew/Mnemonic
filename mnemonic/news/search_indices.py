from django.conf import settings
from django.core.validators import EMPTY_VALUES

from elasticsearch_dsl import Document, analyzer, Text, Date, Keyword
from elasticsearch_dsl.connections import connections
from retry import retry

from mnemonic.news.utils.string_utils import get

connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS)
article_analyzer = analyzer('article_analyzer',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
)

class News(Document):
    news_type = Text(analyzer='keyword', fields={'raw': Keyword()})
    source = Text(analyzer='standard', fields={'raw': Keyword()})
    source_type = Text(analyzer='keyword', fields={'raw': Keyword()})
    mentions = Text(analyzer='standard', fields={'raw': Keyword(multi=True)}, multi=True)
    title = Text(analyzer=article_analyzer)
    body = Text(analyzer=article_analyzer)
    published_on = Date()
    url = Text(fields={'keyword': Keyword()})

    class Index:
        name = 'news'

    class Meta:
        doc_type = '_doc'


class NewsIndexable(object):
    INDEX_NEWS_TYPE_FIELD = None
    INDEX_SOURCE_FIELD = None
    INDEX_SOURCE_TYPE_FIELD = None
    INDEX_MENTIONS_FIELD = None
    INDEX_TITLE_FIELD = None
    INDEX_BODY_FIELD = None
    INDEX_PUBLISHED_ON_FIELD = None
    INDEX_URL_FIELD = None

    def get_index_meta_data(self):
        return {'id': self.get_uid()}

    def get_index_data(self):
        d = {
            'news_type': get(self, self.INDEX_NEWS_TYPE_FIELD),
            'source': get(self, self.INDEX_SOURCE_FIELD),
            'source_type': get(self, self.INDEX_SOURCE_TYPE_FIELD),
            'mentions': get(self, self.INDEX_MENTIONS_FIELD),
            'title': get(self, self.INDEX_TITLE_FIELD),
            'body': get(self, self.INDEX_BODY_FIELD),
            'published_on': get(self, self.INDEX_PUBLISHED_ON_FIELD),
            'url': get(self, self.INDEX_URL_FIELD),
        }
        return {k: v for k,v in d.items() if v not in EMPTY_VALUES}

    def push_to_index(self):

        @retry(tries=10, delay=1, backoff=2)
        def f(obj):
            obj.save()

        news = News(meta=self.get_index_meta_data(), **self.get_index_data())
        f(news)

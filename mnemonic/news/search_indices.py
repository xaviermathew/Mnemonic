from django.conf import settings
from django.core.validators import EMPTY_VALUES

from elasticsearch_dsl import Document, analyzer, Text, Date, Keyword, tokenizer
from elasticsearch_dsl.connections import connections
from retry import retry

from mnemonic.news.utils.string_utils import get

connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS)
article_analyzer = analyzer('article_analyzer',
    tokenizer=tokenizer('article_tokenizer', "uax_url_email", max_token_length=2048),
    filter=["lowercase", "stop", "snowball"],
)

class News(Document):
    source = Keyword()
    source_type = Keyword()
    mentions = Keyword(multi=True)
    title = Text(analyzer=article_analyzer)
    body = Text(analyzer=article_analyzer)
    published_on = Date()
    url = Keyword(ignore_above=2048)

    class Index:
        name = 'news'

    class Meta:
        doc_type = '_doc'


class NewsIndexable(object):
    INDEX_SOURCE_FIELD = None
    INDEX_SOURCE_TYPE_FIELD = None
    INDEX_MENTIONS_FIELD = None
    INDEX_TITLE_FIELD = None
    INDEX_BODY_FIELD = None
    INDEX_PUBLISHED_ON_FIELD = None
    INDEX_URL_FIELD = None

    BULK_FETCH_CHUNK_SIZE = 10 * 1000
    BULK_INDEX_CHUNK_SIZE = 10 * 1000

    def get_index_meta_data(self):
        return {'id': self.get_uid()}

    def get_index_data(self):
        d = {
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

    @classmethod
    def get_bulk_index_qs(cls):
        return cls.objects.filter(is_pushed_to_index=False)

    @classmethod
    def get_bulk_index_data(cls):
        from django.db import models
        from mnemonic.news.utils.queryset_utils import queryset_iterator

        if issubclass(cls, models.Model):
            qs = queryset_iterator(cls.get_bulk_index_qs(), chunksize=cls.BULK_FETCH_CHUNK_SIZE)
            return (obj.get_index_data() for obj in qs)
        else:
            raise NotImplementedError

    @classmethod
    def bulk_push_to_index(cls):
        from elasticsearch.helpers import bulk
        from mnemonic.news.utils.search_utils import get_connection

        connection = get_connection()
        data = cls.get_bulk_index_data()
        objects = (News.create(d).to_dict(include_meta=True) for d in data)
        return bulk(connection, objects, chunk_size=cls.BULK_INDEX_CHUNK_SIZE, timeout=100)

import copy
from datetime import datetime

from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

from django.conf import settings

ES_CLIENT = None


def get_connection():
    global ES_CLIENT
    if ES_CLIENT is None:
        ES_CLIENT = connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS)
    return ES_CLIENT


def get_client():
    client = get_connection()
    return Search(using=client, index="news")


def serialize_search_results(results):
    for result in results:
        d = copy.deepcopy(result._d_)
        d['meta'] = copy.deepcopy(result.meta._d_)
        if 'published_on' in d:
            d['published_on'] = datetime.fromisoformat(d['published_on'])
        yield d


def filter_values(s, field_name, values):
    q_set = [Q('match', **{field_name: v}) for v in values]
    s = s.query('bool', should=q_set)
    return s


def get_search_results(query=None, news_types=None, newspapers=None, twitter_handles=None,
                       twitter_mentions=None, start_date=None, end_date=None):
    s = get_client()
    if query and query[0]:
        s = s.filter("simple_query_string", query=query[0], fields=['title', 'body'])
    if news_types:
        s = filter_values(s, 'news_type.raw', news_types)
    if newspapers or twitter_handles:
        sources = (newspapers or []) + (twitter_handles or [])
        s = filter_values(s, 'source.raw', sources)
    if twitter_mentions:
        s = filter_values(s, 'mentions.raw', twitter_mentions)
    if (start_date and start_date[0]) or (end_date and end_date[0]):
        published_on = {}
        if start_date and start_date[0]:
            published_on['gte'] = start_date[0]
        if end_date and end_date[0]:
            published_on['lte'] = end_date[0]
        s = s.query('range', published_on=published_on)

    s = s.sort('-published_on')
    serialized = serialize_search_results(s[:100])
    return s.count(), serialized

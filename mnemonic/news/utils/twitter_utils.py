from retry import retry
import twint
from twint.tweet import tweet as Tweet
from tqdm import tqdm

from django.conf import settings

from mnemonic.news.utils.cache_utils import DiskCacheManager
from mnemonic.news.utils.msgpack_utils import streaming_loads, dumps
from mnemonic.news.utils.string_utils import slugify


def get_crawl_fname(prefix, signature_parts):
    s = slugify('_'.join(signature_parts), retain_punct={'@'})
    return prefix % s


def update_seen_tweets_disk_cache(since=None):
    from mnemonic.news.models import Tweet

    filters = {}
    if since:
        filters['created_on__gte'] = since
    qs = Tweet.objects.filter(**filters).values_list('tweet_id', flat=True)
    return qs.iterator()


class CrawlBuffer(object):
    def __init__(self, signature_parts, only_new=True):
        self.id = '_'.join(signature_parts)
        self.fname = get_crawl_fname('state/twint/results_%s.msgpack', signature_parts)
        self.file = open(self.fname, 'ab')
        self.only_new = only_new
        if only_new:
            self.seen = DiskCacheManager.get(settings.DISK_CACHE_SEEN_TWEETS)

    def append(self, tweet):
        self.file.write(dumps(vars(tweet)))

    def get_data(self):
        self.file.flush()
        self.file.close()
        data = streaming_loads(open(self.fname, 'rb'))
        for d in tqdm(data, desc='reading tweets:%s' % self.id):
            if self.only_new and d['id'] in self.seen:
                continue
            t = Tweet()
            for k, v in d.items():
                if isinstance(v, str):
                    v = v.replace('\u0000', '')
                t.__dict__[k] = v
            yield t


@retry(tries=1000)
def get_tweets_for_username(username, limit=None, since=None, until=None, mentions=False, language=None, only_cached=False):
    c = twint.Config()
    if mentions:
        c.Search = '@' + username
        signature_parts = [c.Search]
    else:
        c.Username = username
        signature_parts = [c.Username]

    if limit:
        c.Limit = limit

    if since:
        c.Since = since.strftime('%Y-%m-%d %H:%M:%S')
        signature_parts.append(c.Since)

    if until:
        c.Until = until.strftime('%Y-%m-%d %H:%M:%S')
        signature_parts.append(c.Until)

    if language:
        c.Lang = language

    c.Store_object = True
    c.Store_object_tweets_list = CrawlBuffer(signature_parts)
    c.Resume = get_crawl_fname('state/twint/resume_%s.txt', signature_parts)
    if not only_cached:
        twint.run.Search(c)
    return c.Store_object_tweets_list.get_data()

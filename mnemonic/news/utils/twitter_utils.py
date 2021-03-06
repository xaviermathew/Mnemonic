import gzip
import logging

from retry import retry
import twint
from twint.tweet import tweet as Tweet
from tqdm import tqdm

from django.conf import settings

from mnemonic.news.utils.cache_utils import DiskCacheManager
from mnemonic.news.utils.msgpack_utils import streaming_loads, dumps
from mnemonic.news.utils.string_utils import slugify

_LOG = logging.getLogger(__name__)


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
    def __init__(self, signature_parts, only_new=True, buffer_size=25 * 1000):
        self.signature_parts = signature_parts
        self.id = '_'.join(signature_parts)
        self.fname = get_crawl_fname('state/twint/results_%s.msgpack.gz', signature_parts)
        self.file = gzip.open(self.fname, 'ab')
        self.buffer = []
        self.buffer_size = buffer_size
        self.only_new = only_new
        if only_new:
            self.seen = DiskCacheManager.get(settings.DISK_CACHE_SEEN_TWEETS)

    @property
    def resume_fname(self):
        return get_crawl_fname('state/twint/resume_%s.txt', self.signature_parts)

    def flush(self):
        _LOG.info('flushing buffer for [%s]', self.fname)
        self.file.write(dumps(self.buffer))
        self.buffer = []

    def append(self, tweet):
        self.buffer.append(vars(tweet))
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def close(self):
        if self.buffer:
            self.flush()
        self.file.flush()
        self.file.close()

    def get_data(self):
        self.close()
        data = streaming_loads(gzip.open(self.fname, 'rb'))
        for d_set in tqdm(data, desc='reading tweets:%s' % self.id):
            for d in d_set:
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
    c.Resume = c.Store_object_tweets_list.resume_fname
    if not only_cached:
        twint.run.Search(c)
    return c.Store_object_tweets_list.get_data()

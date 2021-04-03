import gzip
import logging

from retry import retry
import twint
from twint.tweet import tweet as Tweet
from tqdm import tqdm

from mnemonic.news.utils.msgpack_utils import streaming_loads2 as streaming_loads, dumps
from mnemonic.news.utils.string_utils import slugify

_LOG = logging.getLogger(__name__)
GZIP_FILES = False


def get_crawl_fname(prefix, signature_parts):
    s = slugify('_'.join(signature_parts), retain_punct={'@'})
    return prefix % s


class CrawlBuffer(object):
    def __init__(self, username, limit=None, since=None, until=None, mentions=False,
                 language=None, only_cached=False, buffer_size=25 * 1000):
        c = twint.Config()
        if mentions:
            c.Search = '@' + username
            signature_parts = [c.Search]
        else:
            c.Username = username
            signature_parts = [c.Username]

        if since:
            c.Since = since

        if until:
            c.Until = until

        if limit:
            c.Limit = limit

        if language:
            c.Lang = language

        c.Store_object = True
        c.Store_object_tweets_list = self

        self.twint_config = c
        self.signature_parts = signature_parts

        c.Resume = get_crawl_fname('state/twint/resume_%s.txt', self.signature_parts)
        self.resume_fname = c.Resume

        self.id = '_'.join(signature_parts)
        if GZIP_FILES:
            self.fname = get_crawl_fname('state/twint/results_%s.msgpack.gz', signature_parts)
            self.file = gzip.open(self.fname, 'ab')
        else:
            self.fname = get_crawl_fname('state/twint/results_%s.msgpack', signature_parts)
            self.file = open(self.fname, 'ab')
        self.buffer = []
        self.buffer_size = buffer_size
        self.only_cached = only_cached

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

    @retry(tries=1000)
    def start_crawl(self):
        if not self.only_cached:
            twint.run.Search(self.twint_config)

    def get_data(self):
        self.close()
        if GZIP_FILES:
            data = streaming_loads(gzip.open(self.fname, 'rb'))
        else:
            data = streaming_loads(open(self.fname, 'rb'))
        for d_set in tqdm(data, desc='reading tweets:%s' % self.id):
            if isinstance(d_set, list) and d_set and isinstance(d_set[0], dict) and 'conversation_id' in d_set[0]:
                for d in d_set:
                    t = Tweet()
                    for k, v in d.items():
                        if isinstance(v, str):
                            v = v.replace('\u0000', '')
                        t.__dict__[k] = v
                    yield t

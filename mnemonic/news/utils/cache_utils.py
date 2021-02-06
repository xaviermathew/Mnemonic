import hashlib
import os

from lsm import LSM
import requests
from scrapy.extensions.httpcache import FilesystemCacheStorage
from tqdm import tqdm
from urlnormalizer import normalize_url

from django.conf import settings

from mnemonic.news.utils.class_utils import get_object_from_python_path
from mnemonic.news.utils.file_utils import ShelveFile, mkdir_p


class DownloadCache(object):
    def __init__(self, url):
        self.original_url = url
        self.url = normalize_url(url)
        self.url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        self.cache_path = os.path.join(settings.ARTICLE_CACHE_DIR, self.url_hash)

    def is_cached(self):
        return os.path.exists(self.cache_path)

    def cache(self, html):
        if not isinstance(html, str):
            html = str(html)
        mkdir_p(os.path.dirname(self.cache_path))
        with ShelveFile(self.cache_path) as f:
            f.write(html)

    def _get(self):
        return open(self.cache_path).read()

    def get(self):
        if self.is_cached():
            return self._get()

        r = requests.get(self.url)
        html = r.text
        self.cache(html)
        return html


class DownloadCacheStorage(FilesystemCacheStorage):
    def store_response(self, spider, request, response):
        DownloadCache(request.url).cache(response.body)
        return super(DownloadCacheStorage, self).store_response(spider, request, response)

    def retrieve_response(self, spider, request):
        response = super(DownloadCacheStorage, self).retrieve_response(spider, request)
        if response and response.status >= 400:
            return None
        else:
            return response


class DiskCacheManager(object):
    @classmethod
    def get(cls, name):
        path = settings.DISK_CACHE_ROOT + name + '.ldb'
        return LSM(path)

    @classmethod
    def update(cls, name, **kwargs):
        cfg = settings.DISK_CACHES[name]
        fn = get_object_from_python_path(cfg['fn'])
        data = fn(**kwargs)
        cache = cls.get(name)
        if cfg['type'] == 'set':
            items = tqdm(data, desc='updating diskcache:%s' % name)
            cache.update({item: True for item in items})

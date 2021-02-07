from collections import defaultdict
import logging

from tqdm import tqdm

from django.db import models, IntegrityError

_LOG = logging.getLogger(__name__)


class CachedManager(models.Manager):
    use_in_migrations = True

    def __init__(self, *args, **kwargs):
        super(CachedManager, self).__init__(*args, **kwargs)
        self._cache = defaultdict(dict)

    def clear_cache(self):
        self._cache.clear()

    def get_cached(self, **kwargs):
        key, value = next(iter(kwargs.items()))
        try:
            obj = self._cache[self.db][value]
        except KeyError:
            obj = self.get(**kwargs)
            self._cache[self.db][key] = obj
        return obj


def bulk_create(objs, should_bulk_create=True):
    model = objs[0].__class__

    if should_bulk_create:
        model.objects.bulk_create(objs, ignore_conflicts=True)
    else:
        for obj in tqdm(objs, desc='bulk_create_fallback:%s' % model):
            try:
                obj.save()
            except IntegrityError as ex:
                if 'duplicate key value violates unique constraint' in ex.args[0]:
                    _LOG.info('[%s] obj already exists', model)
                else:
                    raise ex
    return objs

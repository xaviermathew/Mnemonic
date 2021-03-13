from collections import defaultdict
from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType

from mnemonic.core.admin import BaseAdmin
from mnemonic.news.models import Article, Feed, NewsSource, TwitterJob


@admin.register(Article)
class ArticleAdmin(BaseAdmin):
    list_display = ['feed', 'title', 'published_on']
    list_filter = ['feed__source', 'is_top_news', 'is_pushed_to_index']


@admin.register(NewsSource)
class NewsSourceAdmin(BaseAdmin):
    list_display = ['name']


@admin.register(Feed)
class FeedAdmin(BaseAdmin):
    list_display = ['name', 'source', 'is_top_news']
    list_filter = ['source', 'is_top_news']
    actions = ['crawl_feed']

    def crawl_feed(self, request, qs):
        messages.add_message(request, messages.INFO, 'Crawl for [%s] feed(s) has been queued' % len(qs))
        for feed in qs:
            feed.crawl_feed_async()


class TweetEntityFilter(admin.SimpleListFilter):
   title = 'Entity'
   parameter_name = 'entity'
   _cached_lookups = None
   _cached_lookups_map = None

   def _get_lookups(self):
       ct_id_pairs = TwitterJob.objects.order_by('content_type', 'object_id')\
                                       .distinct('content_type', 'object_id')\
                                       .values_list('content_type', 'object_id')
       ct_id_map = defaultdict(set)
       for ct, id in ct_id_pairs:
           ct_id_map[ct].add(id)
       choices = []
       for ct, id_set in ct_id_map.items():
           klass = ContentType.objects.get_for_id(ct).model_class()
           qs = klass.objects.filter(pk__in=id_set).values_list('id', 'name')
           for id, name in qs:
            choices.append(('%s.%s' % (ct, id), '%s:%s' % (klass.__name__, name)))
       return choices

   def lookups(self, request, model_admin):
       if self._cached_lookups is None:
           self._cached_lookups = self._get_lookups()
           self._cached_lookups_map = dict(self._cached_lookups)
       return self._cached_lookups

   def queryset(self, request, queryset):
       value = self.value()
       if value and value in self._cached_lookups_map:
           ct, id = value.split('.')
           queryset = queryset.filter(content_type=ct, object_id=id)
       return queryset


@admin.register(TwitterJob)
class TwitterJobAdmin(BaseAdmin):
    list_display = ['entity', 'is_crawled', 'is_pushed_to_index', 'config']
    list_filter = [TweetEntityFilter, 'is_crawled', 'is_pushed_to_index']

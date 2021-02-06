ARTICLE_CACHE_DIR = 'data/cache/articles/'
ARTICLE_ARCHIVE_CACHE_DIR = 'data/cache/article_archive/'
FEED_SOURCE_GOOGLE_SHEET_ID = None
SHOULD_LIMIT_ARCHIVE_CRAWL = False

DISK_CACHE_ROOT = 'state/disk_cache/'
DISK_CACHE_SEEN_TWEETS = 'seen_tweets'
DISK_CACHES = {
    DISK_CACHE_SEEN_TWEETS: {
        'fn': 'mnemonic.news.utils.twitter_utils.update_seen_tweets_disk_cache',
        'type': 'set'
    }
}

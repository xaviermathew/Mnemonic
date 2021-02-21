from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db import models
from django.db.models.expressions import RawSQL


class DashboardManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super(DashboardManager, self).get_queryset(*args, **kwargs)
        qs = qs.filter(name__startswith='Story:', is_archived=False, is_draft=False)
        return qs


class Dashboard(models.Model):
    use_db = settings.REDASH_DATABASE
    objects = DashboardManager()
    all_objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'dashboards'

    id = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    org_id = models.IntegerField()
    slug = models.CharField(max_length=140, db_index=True)
    name = models.CharField(max_length=100)
    user_id = models.IntegerField()
    layout = models.TextField()
    dashboard_filters_enabled = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False, db_index=True)
    is_draft = models.BooleanField(default=False, db_index=True)
    tags = ArrayField(models.TextField(), null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.name

    @property
    def cleaned_name(self):
        return self.name[6:]

    @property
    def api_key(self):
        try:
            api_key = APIKey.objects.get(object_type='dashboards', object_id=self.id, active=True)
        except APIKey.DoesNotExist:
            pass
        else:
            return api_key.api_key

    @property
    def url(self):
        return settings.REDASH_DASHBOARD_URL + self.api_key

    @property
    def description(self):
        qs = Widget.objects.filter(dashboard_id=self.id)\
                           .annotate(row=RawSQL("(((options::json)->'position')::json->'row')::text", (), models.TextField()),
                              col=RawSQL("(((options::json)->'position')::json->'col')::text", (), models.TextField()))\
                           .filter(row='0', col='0')
        try:
            widget = qs.get()
        except Widget.DoesNotExist:
            pass
        else:
            return widget.text


class APIKey(models.Model):
    use_db = settings.REDASH_DATABASE

    class Meta:
        managed = False
        db_table = 'api_keys'

    id = models.IntegerField(primary_key=True)
    object_id = models.IntegerField()
    object_type = models.CharField(max_length=255)
    org_id = models.IntegerField()
    api_key = models.CharField(db_index=True, max_length=255)
    active = models.BooleanField()
    created_by_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return '[%s:%s] - %s' % (self.object_type, self.object_id, self.api_key)


class Widget(models.Model):
    use_db = settings.REDASH_DATABASE

    class Meta:
        managed = False
        db_table = 'widgets'

    id = models.IntegerField(primary_key=True)
    dashboard_id = models.IntegerField(db_index=True)
    visualization_id = models.IntegerField()
    text = models.TextField()
    width = models.IntegerField()
    options = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.dashboard_id

class DBRouter(object):
    def db_for_read(self, model, **hints):
        return getattr(model, 'use_db', None)

    def db_for_write(self, model, **hints):
        return getattr(model, 'use_db', None)

    def allow_migrate(self, db, app_label, model_name = None, **hints):
        return db == 'default'

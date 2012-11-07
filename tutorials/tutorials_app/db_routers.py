class AuthRouter(object):
    """
    Apps auth and sessions works with auth_db
    """
    _apps = ['sessions', 'auth']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in AuthRouter._apps:
            return 'auth_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in AuthRouter._apps:
            return 'auth_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in AuthRouter._apps or \
                obj2._meta.app_label in AuthRouter._apps:
            return True
        return None

    def allow_syncdb(self, db, model):
        if (db == 'auth_db') or \
           (model._meta.app_label in AuthRouter._apps):
            return False
        return None

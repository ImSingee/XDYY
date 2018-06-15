from wechatpy.session import SessionStorage


class DatabaseStorage(SessionStorage):

    def __init__(self, database, key='key', value='value'):
        self.db = database
        self.key = key
        self.value = value

    def get(self, key, default=None):
        try:
            return self.db.objects.get(**{self.key: key}).__getattribute__(self.value)
        except:
            return default

    def set(self, key, value, ttl=None):
        if value is None:
            return
        d, _ = self.db.objects.get_or_create(**{self.key: key})
        d.__setattr__(self.value, value)
        d.save()

    def delete(self, key):
        try:
            self.db.objects.get(**{self.key: key}).delete()
        except:
            pass

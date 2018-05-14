from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = '用户账户'

    def ready(self):
        super().ready()
        from . import signals

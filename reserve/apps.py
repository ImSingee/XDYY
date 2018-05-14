from django.apps import AppConfig


class ReserveConfig(AppConfig):
    name = 'reserve'
    verbose_name = '预约'

    def ready(self):
        from . import signals

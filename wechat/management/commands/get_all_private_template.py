from django.core.management.base import BaseCommand

from wechat.utils import save_template_info


class Command(BaseCommand):
    help = '从微信平台拉取并保存所有模板消息信息'

    def handle(self, *args, **options):
        save_template_info()

from django.core.management.base import BaseCommand
from reserve.utils import do_repeat_all


class Command(BaseCommand):
    help = '定时任务用，生成重复预约时间记录'

    def handle(self, *args, **options):
        do_repeat_all()

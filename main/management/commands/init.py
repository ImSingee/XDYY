from django.core.management.base import BaseCommand
import init


class Command(BaseCommand):
    help = 'Init Core Data'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, nargs='?')

    def handle(self, *args, **options):
        if options['name'] is None:
            init.init()
        else:
            name = 'init_{}'.format(options['name'])
            getattr(init, name)()

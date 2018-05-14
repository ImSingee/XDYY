import os
from django.test import TestCase
from django.conf import settings
from .utils import GlobalSettings
from account.utils import UserSettings
from init import init_global, init_superuser, init_group


class InitTest(TestCase):
    def setUp(self):
        init_global()
        init_group()
        init_superuser()

    def test_global(self):
        g = GlobalSettings()
        import json
        with open(os.path.join(settings.BASE_DIR, 'init_data', 'global.json'), 'r', encoding='utf-8') as f:
            j = json.load(f)

        for k, v in j.items():
            self.assertEqual(g.get(k), g.wrap(v.get('value')))
            self.assertEqual(g.get_description(k), v.get('description'))

    def test_superuser(self):
        from configparser import ConfigParser
        cf = ConfigParser()
        cf.read(os.path.join(settings.CONFIG_DIR), encoding='utf-8')

        username = cf.get('SUPERUSER', 'username')
        password = cf.get('SUPERUSER', 'password')

        self.assertTrue(UserSettings().check_user_password(username, password))

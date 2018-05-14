from django.test import TestCase
from .utils import GlobalSettings

from .models import Global


# Create your tests here.
class GlobalSettingsTest(TestCase):
    def setUp(self):
        g = Global(key='siteName', value='学导有约|测试')
        g.save()

    def test_get_default(self):
        g = GlobalSettings('siteName')
        self.assertIsNotNone(g.get_default())
        g = GlobalSettings()
        self.assertIsNone(g.get_default('123'))

    def test_get(self):
        g = GlobalSettings('siteName')
        self.assertEqual(g.get('siteName'), Global.objects.get(key='siteName').value)

    def test_wrap(self):
        g = GlobalSettings()
        self.assertIs(type(g.get('siteStatus')), bool)
        self.assertTrue(g.get('siteStatus'))
        self.assertFalse(g.get('loginStatus'))
        self.assertIs(type(g.get('preDayMax')), int)
        self.assertEqual(g.get('preDayMax'), 10)

    def test_set(self):
        g = GlobalSettings()
        g.set('preDayMin')
        self.assertEqual(g.get('preDayMin'), g.get_default('preDayMin'))
        self.assertEqual(g.get_description('preDayMin'), g.get_default_description('preDayMin'))
        g.set('preDayMax', 9, 'des')
        self.assertEqual(g.get('preDayMax'), 9)
        self.assertEqual(g.get_description('preDayMax'), 'des')

        GlobalSettings('test', 't').set(description='d')
        self.assertEqual(GlobalSettings('test').get(), 't')
        self.assertEqual(GlobalSettings('test').get_description(), 'd')



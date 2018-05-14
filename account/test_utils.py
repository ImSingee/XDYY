from django.test import TestCase, TransactionTestCase
from init import init_minimal

from .models import User
from .utils import UserSettings


class UserSettingsTest(TransactionTestCase):
    def setUp(self):
        init_minimal()

    def test_create_user(self):
        us = UserSettings()
        u = us.create_user('Singee', 'Test')
        self.assertIs(type(u), User)

        u = UserSettings()
        u = us.create_user('Singee', 'm')
        self.assertFalse(u)

        us = UserSettings('Test')
        u = us.create_user()
        self.assertIs(type(u), User)

        us = UserSettings('TestM')
        u = us.create_user(password='TestM')
        self.assertTrue(u.check_password('TestM'))

        u = UserSettings().create_user('InfoTest', 'Test', name='超级管理员', email='imsingee@gmail.com')
        self.assertEqual(u.name, '超级管理员')
        self.assertEqual(u.email, 'imsingee@gmail.com')

    def test_create_superuser(self):
        u = UserSettings().create_superuser('SU', 'SU')
        self.assertTrue(u)
        self.assertTrue(u.is_superuser)

    def test_check_user_password(self):
        u = UserSettings().create_user('S1')
        self.assertFalse(u.check_password('m'))
        u = UserSettings().create_user('S2', 'S2')
        self.assertFalse(u.check_password('S1'))
        self.assertTrue(u.check_password('S2'))

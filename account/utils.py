from django.db.utils import IntegrityError
from main.utils import choose_value, Error
from .models import User, UserInfo

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group


class UserSettings:
    def __init__(self, *, user_obj=None, username=None, **kwargs):
        if user_obj is not None:
            self.user = user_obj
            self.username = self.user.username
            self.email = self.user.email

        # username 加入 kwargs
        self.username = username

        if self.username is not None:
            kwargs.update({'username': username})
        # email
        if 'email' in kwargs:
            self.email = kwargs['email']
        # 忽略密码验证
        if 'password' in kwargs:
            kwargs.pop('password')
        # self.user
        self.user = None
        if choose_value(*kwargs.values(), allow_none=True) is not None:
            try:
                self.user = User.objects.get(**kwargs)
            except User.DoesNotExist:
                pass

    def _create_user(self, username=None, password=None, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        extra_fields = extra_fields.copy()
        extra_user_fields = {}
        extra_userinfo_fields = {}
        username = User.normalize_username(choose_value(username, self.username))
        email = User.normalize_email(
            choose_value(extra_fields.get('email'), getattr(self, 'email', None), allow_none=True))
        if email is not None:
            extra_fields['email'] = email

        user_fields = [x.name for x in User._meta.get_fields()]
        user_info_fields = [x.name for x in UserInfo._meta.get_fields()]

        for k, v in extra_fields.items():
            if k in user_info_fields:
                extra_userinfo_fields.update({k: v})
            if k in user_fields:
                extra_user_fields.update({k: v})

        user = User(username=username, **extra_user_fields)
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)
        try:
            user.save()
        except IntegrityError as e:
            return Error(msg='IntegrityError - 可能是用户名重复引起的', error=e)

        userinfo = user.userinfo
        for k, v in extra_userinfo_fields.items():
            setattr(userinfo, k, v)
        userinfo.save()
        return user

    def create_admin(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_staff') is not True:
            return Error(msg='Superuser must have is_staff=True.')
        u = self.create_user(username=username, password=password, **extra_fields)
        if u is not None:
            self.add_group(user_obj=u, id=1)
        else:
            return u

    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_student(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('reserver', True)
        extra_fields.setdefault('reservee', False)
        extra_fields.setdefault('auth_name', extra_fields.get('name', ''))
        u = self.create_user(username, password, **extra_fields)
        if u:
            self.add_group(user_obj=u, id=3)  # reserver
        return u

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            return Error(msg='Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            return Error(msg='Superuser must have is_superuser=True.')

        u = self._create_user(username, password, **extra_fields)
        # print(u)
        if u is not None:
            self.add_group(user_obj=u, id=1)

        return u

    def check_user_password(self, username=None, password=None):
        username = choose_value(username, self.username)
        if password is None:
            return False
        u = User.objects.filter(username=username)
        if not u.exists():
            return False
        else:
            u = u.first()
        return u.check_password(password)

    def login(self, request, username=None, password=None, force=False):
        username = choose_value(username, self.username)
        if not password and not force:
            return False
        user = authenticate(request, username=username, password=password, force=force)
        if user is not None:
            login(request, user)
            return True
        else:
            return False

    def add_group(self, *, user_obj=None, id=None, name=None, **kwargs):
        """
        本函数必须提前初始化 self.user 或提供 user_obj
        """
        user_obj = choose_value(user_obj, self.user)
        if not user_obj:
            raise ValueError('user_obj 未初始化')
        kwargs = kwargs.copy()
        if id is not None:
            kwargs.update({'id': id})
        if name is not None:
            kwargs.update({'name': name})
        user_obj.groups.add(Group.objects.get(**kwargs))


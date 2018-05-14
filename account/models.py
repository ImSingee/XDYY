import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from reserve.models import ReserveRecord


# Create your models here.

class User(AbstractUser):
    GENDER_CHOICES = (
        (-1, '未知'),
        (1, '男'),
        (2, '女'),
    )
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.IntegerField(verbose_name='性别', choices=GENDER_CHOICES, default=-1)
    tel = models.CharField(max_length=60, verbose_name='电话号码', default='', blank=True)
    id_card_no = models.CharField(max_length=80, verbose_name='身份证号', default='', blank=True)

    avatar = models.ImageField(verbose_name='头像', upload_to='avatars/', default='default/default.png',
                               height_field='avatar_height', width_field='avatar_width')

    avatar_height = models.PositiveIntegerField(null=True, blank=True, editable=False, default="120",
                                                verbose_name='头像高度')
    avatar_width = models.PositiveIntegerField(null=True, blank=True, editable=False, default="120",
                                               verbose_name='头像宽度')

    def __str__(self):
        return '<User {}#>{}{}'.format(self.id, self.username, ' | {}'.format(self.name) if self.name else '')

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name + '@' + domain_part.lower()
        return email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            if not os.path.isfile(self.avatar.path):
                return
            from PIL import Image
            with Image.open(self.avatar.path) as im:
                x, y = im.size
                size = (100, 100)
                im.thumbnail((120, 120 * y / x), resample=Image.LANCZOS)
                im.save(self.avatar.path)

    def get_role(self):
        if self.is_superuser:
            return '超级管理员'
        elif self.is_staff:
            return '管理员'
        else:
            return '未知身份'

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')

    # 身份
    reserver = models.BooleanField(verbose_name='预约人', default=False)
    reservee = models.BooleanField(verbose_name='被预约人', default=False)

    # reserver
    auth_code = models.CharField(verbose_name='预约人编码', null=True, blank=True, max_length=80)
    auth_name = models.CharField(verbose_name='预约人姓名', null=True, blank=True, max_length=80)

    # reservee
    can_reserved = models.BooleanField(verbose_name='可被预约', default=False)
    RESERVEE_TYPE_CHOICES = (
        (1, '学导'),
        (2, '老师'),
    )
    reservee_type = models.IntegerField(verbose_name='被预约人种类', choices=RESERVEE_TYPE_CHOICES, default=1)
    GENDER_CHOICES = (
        (0, '不限'),
        (1, '仅限男性'),
        (2, '仅限女性'),
    )
    can_reserve_gender = models.IntegerField(verbose_name='可接受预约人性别', help_text='对于未定义性别的用户只有不限性别选项可被预约',
                                             choices=GENDER_CHOICES, default=0)
    short_intro = models.TextField(verbose_name='简介（显示于头像下方）', null=True, blank=True, )
    intro = models.TextField(verbose_name='介绍', null=True, blank=True, )
    default_address = models.CharField(verbose_name='默认地点', null=True, blank=True, max_length=160)
    can_reserve_type = models.ManyToManyField('reserve.ReserveType', blank=True, verbose_name='可被预约种类')

    @property
    def reservee_rank_average(self):
        # TODO 缓存得分
        all = ReserveRecord.objects.filter(status=200, reserver_mark__isnull=False, main_time__reservee__userinfo=self)
        if not all.exists():
            return -2  # 暂无评分数据
        # elif len(all) < 10:
        #     return -1  # 评分数据不足

        return all.aggregate(models.Avg('reserver_mark')).get('reserver_mark__avg')

    @property
    def reservee_rank_average_msg(self):
        return {
            -2: '暂无评分数据',
            -1: '评分数据不足',
            0: '☆☆☆☆☆',
            1: '★☆☆☆☆',
            2: '★★☆☆☆',
            3: '★★★☆☆',
            4: '★★★★☆',
            5: '★★★★★',
        }.get(round(self.reservee_rank_average))

    # archive（存档数据，不显示）
    zhuanye = models.CharField(verbose_name='专业', max_length=80, default='', blank=True)
    banji = models.CharField(verbose_name='班级', max_length=80, default='', blank=True)

    class Meta:
        verbose_name = '用户额外信息'
        verbose_name_plural = verbose_name

from django.db import models


class WechatConfig(models.Model):
    key = models.CharField(max_length=1024, unique=True)
    value = models.CharField(max_length=1024, default='', blank=True)

    note = models.TextField(default='', blank=True)

    enabled = models.BooleanField(default=True)

    @classmethod
    def get_value(cls, key):
        try:
            value = cls.objects.get(key=key, enabled=True).value
            try:
                return int(value)
            except:
                pass

        except cls.DoesNotExist:
            return None

        if str(value).lower() in ('true', 'yes'):
            return True
        elif str(value).lower() in ('false', 'no'):
            return False

        return value

    @classmethod
    def set_value(cls, key, value='', note='', force=False):

        obj, created = cls.objects.get_or_create(key=key)

        if force or created:
            obj.value = value
            obj.note = note
            obj.save()

        return obj

    class Meta:
        verbose_name = '微信设置'
        verbose_name_plural = verbose_name


class TemplateMessageTemplate(models.Model):
    template_id = models.CharField(verbose_name='模板 ID', max_length=2048)
    title = models.CharField(verbose_name='模板标题', max_length=2048)
    content = models.TextField(verbose_name='内容')

    class Meta:
        verbose_name = '模板消息模板'
        verbose_name_plural = verbose_name


class TemplateMessageTrigger(models.Model):
    template = models.ForeignKey(TemplateMessageTemplate, models.SET_NULL, null=True, blank=True)

    TYPE_CHOICES = (
        (-1, '未定义'),
        (201, 'TO预约人 - 预约提交成功'),
        (202, 'TO预约人 - 预约被拒绝'),
        (203, 'TO预约人 - 预约被取消'),
        (204, 'TO预约人 - 预约被确认'),
        (205, 'TO预约人 - 预约已完成'),
        (206, 'TO预约人 - 预约被标记为无故不出席'),
        (211, 'TO预约人 - 预约即将开始提醒'),
        (301, 'TO被预约人 - 收到预约'),
        (302, 'TO被预约人 - 预约未即时确认提醒'),
        (303, 'TO被预约人 - 预约超时取消提醒'),
        (304, 'TO被预约人 - 预约完成提醒'),
        (311, 'TO被预约人 - 预约即将开始提醒'),
    )
    type = models.IntegerField(verbose_name='类别', choices=TYPE_CHOICES)

    first = models.TextField(default='', blank=True)
    first_color = models.CharField(max_length=64, default='', blank=True)
    keyword1 = models.TextField(default='', blank=True)
    keyword1_color = models.CharField(max_length=64, default='', blank=True)
    keyword2 = models.TextField(default='', blank=True)
    keyword2_color = models.CharField(max_length=64, default='', blank=True)
    keyword3 = models.TextField(default='', blank=True)
    keyword3_color = models.CharField(max_length=64, default='', blank=True)
    keyword4 = models.TextField(default='', blank=True)
    keyword4_color = models.CharField(max_length=64, default='', blank=True)
    keyword5 = models.TextField(default='', blank=True)
    keyword5_color = models.CharField(max_length=64, default='', blank=True)
    keyword6 = models.TextField(default='', blank=True)
    keyword6_color = models.CharField(max_length=64, default='', blank=True)
    remark = models.TextField(default='', blank=True)
    remark_color = models.CharField(max_length=64, default='', blank=True)

    url = models.CharField(max_length=1024, default='', blank=True)
    mini_program = models.CharField(max_length=1024, default='', blank=True)

    class Meta:
        verbose_name = '模板消息触发器'
        verbose_name_plural = verbose_name


class SessionStorage(models.Model):
    key = models.CharField(max_length=1024, unique=True)
    value = models.CharField(max_length=102400, default='', blank=True)

    class Meta:
        verbose_name = '微信 SessionKey 存储'
        verbose_name_plural = verbose_name


class WechatUser(models.Model):
    user = models.OneToOneField('account.User', models.CASCADE, related_name='wechat')
    openid = models.CharField(max_length=1024, blank=True, default='')

    enabled = models.BooleanField(default=False)

    @property
    def binded(self):
        return self.enabled and self.openid

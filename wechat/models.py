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

    def set(self, template_id=None):
        template_id = template_id or self.template_id
        assert template_id, '模板 ID 必填'

    class Meta:
        verbose_name = '模板消息模板'
        verbose_name_plural = verbose_name


class SessionStorage(models.Model):
    key = models.CharField(max_length=1024, unique=True)
    value = models.CharField(max_length=102400, default='', blank=True)

    class Meta:
        verbose_name = '微信 SessionKey 存储'
        verbose_name_plural = verbose_name


class WechatUser(models.Model):
    user = models.OneToOneField('account.User', models.CASCADE, related_name='wechat')
    openid = models.CharField(max_length=1024)

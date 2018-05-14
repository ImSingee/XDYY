from django.db import models


# Create your models here.

class Global(models.Model):
    key = models.CharField(max_length=80, unique=True, verbose_name='键')
    value = models.CharField(max_length=80, verbose_name='值')
    description = models.TextField(default='', verbose_name='说明')
    order = models.IntegerField(verbose_name='显示顺序', default=99)

    # time_added = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    # time_edited = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    def __str__(self):
        return '<全局设置>{}'.format(self.key)

    class Meta:
        verbose_name = '全局设置'
        verbose_name_plural = '全局设置'

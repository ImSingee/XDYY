from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch


# Create your models here.
class Menu(models.Model):
    ICON_TYPES = (
        ('fa fa-{name}', 'Font Awesome'),
    )

    name = models.CharField(verbose_name='显示名', max_length=60)

    icon_name = models.CharField(verbose_name='图标名称', max_length=80, default='', blank=True)
    icon_type = models.CharField(verbose_name='图标类型', choices=ICON_TYPES, max_length=30, default='fa fa-{name}')

    pattern = models.CharField(verbose_name='菜单相对名称', max_length=150, blank=True, null=True)
    path = models.CharField(verbose_name='菜单相对路径', max_length=150, blank=True, null=True)

    auth = models.CharField(verbose_name='权限', max_length=128, blank=True, null=True)

    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, blank=True, null=True,
                               verbose_name='父菜单')

    order = models.IntegerField(verbose_name='顺序', default=99)

    show = models.BooleanField(verbose_name='显示', default=True)

    @property
    def icon(self):
        return self.icon_type.format(name='angle-right' if not self.icon_name else self.icon_name)

    @icon.setter
    def icon(self, value):
        ls = value.split('-', 1)
        self.icon_type = ls[0] + '-{name}'
        self.icon_name = ls[1]

    @property
    def top(self):
        if self.parent is None:
            return True
        else:
            return False

    @property
    def rank(self):
        if self.top:
            return 1
        else:
            return 2

    @property
    def single(self):
        return not self.children.exists()

    def get_path(self):
        if self.pattern:
            try:
                ps = self.pattern.split(';')
                pattern = ps[0]
                if len(ps) > 1:
                    params = ps[1].split(',')
                    d = {}
                    for param in params:
                        ab = param.split('=')
                        d.setdefault(*ab)
                    return reverse(pattern, kwargs=d)
                else:
                    return reverse(pattern)

            except NoReverseMatch:
                pass
        if not self.path:
            return reverse('dashboard:default')
        else:
            return self.path

    def get_absolute_url(self, request):
        return request.get_absolute_url(self.get_path())

    def __str__(self):
        if self.top:
            return '[TOP]' + self.name
        else:
            return self.parent.name + ' - ' + self.name

    class Meta:
        verbose_name = '主菜单'
        verbose_name_plural = verbose_name
        ordering = ['order']

from django.db import models
from django.contrib.postgres.fields import ArrayField


class ReserveType(models.Model):
    TYPE_CHOICES = (
        (1, '课程辅导类'),
        (2, '非课程辅导类'),
    )
    name = models.CharField(verbose_name='名称', max_length=80)
    hot = models.BooleanField(verbose_name='热搜', default=False, help_text='本功能暂时无效')
    order = models.IntegerField(verbose_name='排序', default=999)

    type = models.IntegerField(verbose_name='类别', choices=TYPE_CHOICES, default=2)
    enabled = models.BooleanField(verbose_name='启用', default=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.get_type_display())

    class Meta:
        verbose_name = '可预约种类'
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']


class ReserveTime(models.Model):
    reservee = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='被预约人')
    date = models.DateField(verbose_name='预约日期')
    start_time = models.DateTimeField(verbose_name='预约开始时间')
    end_time = models.DateTimeField(verbose_name='预约结束时间')

    repeat = models.ForeignKey('RepeatReserveTime', on_delete=models.SET_NULL, verbose_name='重复预约来源', null=True,
                               blank=True, editable=False)
    enabled = models.BooleanField(verbose_name='启用', default=True)

    @property
    def is_repeat(self):
        if self.repeat is None:
            return False
        else:
            return True

    ed = models.IntegerField(verbose_name='已预约人数', default=0)
    max = models.IntegerField(verbose_name='最大可预约人数', default=2)

    add_user = models.ForeignKey('account.User', on_delete=models.SET_NULL, related_name='reservetimelog', null=True,
                                 editable=False, verbose_name='添加人', blank=True)

    time_add = models.DateTimeField(verbose_name='添加时间', auto_now_add=True, editable=False)
    time_edit = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True, blank=True, editable=False)

    def __str__(self):
        return '[{}# {}]{} {}-{}'.format(self.reservee.id, self.reservee.name, self.date.strftime('%Y-%m-%d'),
                                         self.start_time.strftime('%H:%M'), self.end_time.strftime('%H:%M'))

    class Meta:
        verbose_name = '可预约时间'
        verbose_name_plural = verbose_name


class RepeatReserveTime(models.Model):
    reservee = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='被预约人',
                                 editable=True)

    start_time = models.TimeField(verbose_name='预约开始时间')
    end_time = models.TimeField(verbose_name='预约结束时间')

    REPEAT_CHOICES = (
        (1, '每周一'),
        (2, '每周二'),
        (3, '每周三'),
        (4, '每周四'),
        (5, '每周五'),
        (6, '每周六'),
        (7, '每周日'),
    )

    repeat = ArrayField(
        models.IntegerField(choices=REPEAT_CHOICES),
        size=7,
        verbose_name='重复选项',
        null=True,
        blank=True,
        help_text='重复选项，1-7 分别代表星期一至星期日重复，使用半角逗号分隔'
    )

    enabled = models.BooleanField(verbose_name='启用', default=True)

    max = models.IntegerField(verbose_name='最大可预约人数', default=2)

    add_user = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, editable=False, blank=True,
                                 related_name='+', verbose_name='添加人')

    time_add = models.DateTimeField(verbose_name='添加时间', auto_now_add=True, editable=False)
    time_edit = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True, blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = '可预约时间（重复）'
        verbose_name_plural = verbose_name


class ReserveRecord(models.Model):
    reserver = models.ForeignKey('account.User', on_delete=models.SET_NULL, verbose_name='预约人', null=True, blank=False)
    main_time = models.ForeignKey(ReserveTime, verbose_name='主预约时间', related_name='+', on_delete=models.SET_NULL,
                                  null=True, blank=False)
    time = models.ManyToManyField(ReserveTime, verbose_name='预约时间', related_name='+')
    type = models.ManyToManyField(ReserveType, verbose_name='内容类别')
    content = models.TextField(verbose_name='内容详情')

    STATUS_TYPE = (
        (-201, '预约人未出席'),
        (-101, '预约人取消预约'),
        (-102, '被预约人取消预约'),
        (-103, '管理员取消预约'),
        (-104, '被预约人超时未答复自动取消预约'),
        (0, '预约已提交'),
        (100, '预约已确认'),
        (200, '预约已完成'),

    )
    status = models.IntegerField(verbose_name='状态', default=0, choices=STATUS_TYPE)

    @property
    def is_canceled(self):
        if self.status < 0:
            return True
        else:
            return False

    @property
    def is_submited(self):
        if self.status in (0,):
            return True
        else:
            return False

    @property
    def is_confirmed(self):
        if self.status in (100,):
            return True
        else:
            return False

    @property
    def is_completed(self):
        if self.status in (200,):
            return True
        else:
            return False

    @property
    def has_confirmed(self):
        if self.confirm_time is not None:
            return True
        else:
            return False

    @property
    def order(self):
        if self.has_confirmed:
            return self.confirm_time
        else:
            return self.time.order_by('-start_time').first()

    @property
    def order_date(self):
        if self.order is None:
            return None
        else:
            return self.order.date

    @property
    def order_datetime(self):
        return self.order.start_time

    @property
    def reservee(self):
        if not self.time.exists():
            return None
        else:
            return self.time.first().reservee

    confirm_time = models.ForeignKey(ReserveTime, verbose_name='确认的预约时间', on_delete=models.SET_NULL, null=True,
                                     blank=True, )

    address = models.ForeignKey('ReservePlace', on_delete=models.SET_NULL, null=True, blank=False, editable=True,
                                related_name='+', verbose_name='预约地点')

    MARK_CHOICES = zip(range(1, 6), range(1, 6))
    reserver_mark = models.IntegerField(verbose_name='预约人评分', choices=MARK_CHOICES, null=True, blank=True,
                                        editable=False)
    reserver_note = models.CharField(verbose_name='预约人留言', max_length=10000, editable=False, null=True, blank=True)

    reserver_mark_time = models.DateTimeField(verbose_name='预约人评分时间', editable=False, null=True, blank=True)

    @property
    def reserver_marked(self):
        return self.reserver_mark is not None

    reservee_mark = models.IntegerField(verbose_name='被预约人评分', choices=MARK_CHOICES, null=True, blank=True,
                                        editable=False)
    reservee_note = models.CharField(verbose_name='被预约人留言', max_length=10000, editable=False, null=True, blank=True)
    reservee_mark_time = models.DateTimeField(verbose_name='被预约人评分时间', editable=False, null=True, blank=True)

    @property
    def reservee_marked(self):
        return self.reservee_mark is not None

    add_user = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, editable=False, blank=True,
                                 related_name='+', verbose_name='添加人')

    time_add = models.DateTimeField(verbose_name='添加时间', auto_now_add=True, editable=False)
    time_edit = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True, blank=True, editable=False)

    class Meta:
        verbose_name = '预约记录'
        verbose_name_plural = verbose_name


class ReservePlace(models.Model):
    TYPE_CHOICES = (
        (0, '任意'),
        (1, '仅限同性'),
        (2, '仅限异性'),
        (3, '仅限男男'),
        (4, '仅限女女'),
    )
    name = models.CharField(verbose_name='地点名称', max_length=120)
    type = models.IntegerField(verbose_name='地点类型', default=0, choices=TYPE_CHOICES)

    enabled = models.BooleanField(verbose_name='可选', default=True)

    class Meta:
        verbose_name = '可选预约地点'
        verbose_name_plural = verbose_name
        ordering = ['type', 'name']

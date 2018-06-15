from django.contrib import admin

from .models import ReserveType, RepeatReserveTime, ReserveTime, ReserveRecord, ReservePlace


# Register your models here.
@admin.register(ReserveType)
class ReserveTypeAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'type', 'hot', 'enabled']
    list_filter = ['type', 'hot', 'enabled']


@admin.register(ReserveTime)
class ReserveTimeAdmin(admin.ModelAdmin):
    list_display = ['reservee', 'date', 'start_time', 'end_time', 'is_repeat', 'enabled']
    readonly_fields = ('add_user', 'time_add', 'time_edit', 'repeat', 'ed',)
    fieldsets = (
        (None, {'fields': ('reservee',)}),
        ('时间', {'fields': ('date', 'start_time', 'end_time')}),
        ('数量设置', {'fields': ('ed', 'max',)}),
        ('有关信息', {'fields': ('repeat', 'add_user', 'time_add', 'time_edit', 'enabled',)}),
    )
    search_fields = ('date', 'start_time', 'end_time', '=reservee__username', 'reservee__name', '=reservee__id')


@admin.register(RepeatReserveTime)
class RepeatReserveTimeAdmin(admin.ModelAdmin):
    list_display = ['reservee', 'start_time', 'end_time', 'max', 'loop_start', 'loop_end', 'enabled']
    readonly_fields = ('add_user', 'time_add', 'time_edit')

    fieldsets = (
        (None, {'fields': ('reservee',)}),
        ('时间', {'fields': ('start_time', 'end_time', 'repeat')}),
        ('数量设置', {'fields': ('max',)}),
        ('循环起止', {'fields': ('loop_start', 'loop_end')}),
        ('有关信息', {'fields': ('add_user', 'time_add', 'time_edit', 'enabled',)}),
    )


@admin.register(ReserveRecord)
class ReserveRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'reserver_name', 'reservee_name', 'confirm_time', 'content', 'status']
    readonly_fields = (
        'add_user', 'time_add', 'time_edit',
        'reserver_mark', 'reserver_note', 'reserver_mark_time', 'reservee_mark',
        'reservee_note', 'reservee_mark_time',
        'main_time', 'time', 'confirm_time',
    )
    fieldsets = (
        (None, {'fields': ('reserver',)}),
        ('预约时间', {'fields': ('main_time', 'time', 'confirm_time')}),
        ('预约内容', {'fields': ('type', 'content')}),
        ('预约状态', {'fields': ('status',)}),
        ('评分信息', {'fields': ('reserver_mark', 'reserver_note', 'reserver_mark_time', 'reservee_mark',
                             'reservee_note', 'reservee_mark_time')}),
        ('有关信息', {'fields': ('add_user', 'time_add', 'time_edit',)}),
    )
    list_filter = ['status']
    filter_horizontal = ('time', 'type')

    # autocomplete_fields = ('main_time',)

    def reserver_name(self, obj):
        return obj.reserver.userinfo.auth_name

    def reservee_name(self, obj):
        if obj.reservee is None:
            return None
        else:
            return obj.reservee.name

    reserver_name.short_description = '预约人姓名'
    reservee_name.short_description = '被预约人姓名'


@admin.register(ReservePlace)
class ReservePlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'enabled']
    ordering = ['type', 'name']

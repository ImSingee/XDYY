from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .models import User, UserInfo


# Register your models here.
@admin.register(User)
class UserAdmin(AuthUserAdmin):
    list_display = ['username', 'email', 'name', 'id_card_no', 'is_staff', 'is_superuser']
    search_fields = ('username', 'name', 'email', 'id_card_no', 'tel')
    list_filter = ('groups', 'is_staff', 'is_superuser', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email',)}),
        (_('Personal info'), {'fields': ('name', 'gender', 'tel', 'id_card_no', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'reserver', 'auth_code', 'auth_name', 'reservee', 'reservee_type', 'can_reserved',
                    'default_address']
    search_fields = (
        'user__username', 'user__name', 'user__email', 'user__id_card_no', 'auth_code', 'auth_name', 'default_address')
    readonly_fields = ('user',)
    list_filter = (
        'reserver', 'reservee', 'reservee_type', 'user__groups', 'user__is_staff', 'user__is_superuser',
        'user__is_active',)
    fieldsets = (
        (None, {'fields': ('user',), }),
        ('身份信息', {'fields': ('reserver', 'reservee',)}),
        ('预约人信息', {'fields': ('auth_code', 'auth_name',)}),
        ('被预约人信息', {'fields': (
            'can_reserved', 'reservee_type', 'can_reserve_gender', 'short_intro', 'intro',
            'can_reserve_type')}),
    )
    filter_horizontal = ('can_reserve_type',)

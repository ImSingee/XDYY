from django.contrib import admin

from .models import WechatConfig, TemplateMessageTemplate, WechatUser


@admin.register(WechatConfig)
class WechatConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'value', 'note', 'enabled']
    list_editable = ('value',)


@admin.register(TemplateMessageTemplate)
class TemplateMessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_id', 'title', 'content']


@admin.register(WechatUser)
class WechatUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'openid', 'enabled']

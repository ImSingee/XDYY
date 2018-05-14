from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Menu


# Register your models here.
def action_hide(modeladmin, request, queryset):
    queryset.update(show=False)


def action_show(modeladmin, request, queryset):
    queryset.update(show=True)


def action_reorder(modeladmin, request, queryset):

    def group(qs):
        result = {}
        ls = list(qs)
        for q in ls:
            if q.top:
                key = -1
            else:
                key = q.parent.id
            if key not in result:
                result.setdefault(key, [])
            result[key].append(q)
        return result

    gs = group(queryset)
    for g in gs.values():
        g.sort(key=lambda x: x.order)
        for i, v in enumerate(g):
            v.order = i
            v.save()


action_hide.short_description = '批量隐藏'
action_show.short_description = '批量显示'
action_reorder.short_description = '批量排序重赋值'

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['get_parent_name', 'name', 'get_icon_html', 'get_path_html', 'rank', 'order', 'show']
    list_display_links = ['name']
    actions = [action_show, action_hide, action_reorder]

    ordering = ['-parent', 'order']

    def get_icon_html(self, obj):
        return format_html('<i class="{}"></i>', obj.icon)

    get_icon_html.short_description = '图标'

    def get_path_html(self, obj):
        return format_html('<a href="{link}">{link}</a>', link=obj.get_path())

    get_path_html.short_description = '跳转路径'

    def get_parent_name(self, obj):
        if obj.parent:
            return format_html('<a href="{}">{}</a>',
                               reverse('admin:dashboard_menu_change', kwargs={'object_id': obj.parent.id}),
                               obj.parent.name)
        else:
            return '-'

    get_parent_name.short_description = '父菜单'
    get_parent_name.admin_order_field = 'parent'

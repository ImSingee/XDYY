# Generated by Django 2.0.3 on 2018-06-15 17:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='显示名')),
                ('icon_name', models.CharField(blank=True, default='', max_length=80, verbose_name='图标名称')),
                ('icon_type', models.CharField(choices=[('fa fa-{name}', 'Font Awesome')], default='fa fa-{name}', max_length=30, verbose_name='图标类型')),
                ('pattern', models.CharField(blank=True, max_length=150, null=True, verbose_name='菜单相对名称')),
                ('path', models.CharField(blank=True, max_length=150, null=True, verbose_name='菜单相对路径')),
                ('order', models.IntegerField(default=99, verbose_name='顺序')),
                ('show', models.BooleanField(default=True, verbose_name='显示')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='dashboard.Menu', verbose_name='父菜单')),
            ],
            options={
                'verbose_name': '主菜单',
                'verbose_name_plural': '主菜单',
                'ordering': ['order'],
            },
        ),
    ]

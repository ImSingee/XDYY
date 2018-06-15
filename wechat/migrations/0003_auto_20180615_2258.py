# Generated by Django 2.0.3 on 2018-06-15 22:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('wechat', '0002_wechatuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='wechatuser',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='wechatuser',
            name='openid',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]
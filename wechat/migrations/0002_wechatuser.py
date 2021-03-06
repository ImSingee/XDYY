# Generated by Django 2.0.3 on 2018-06-15 21:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wechat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WechatUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=1024)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wechat',
                                              to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 2.0.3 on 2018-06-15 23:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('wechat', '0003_auto_20180615_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='first',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='keyword1',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='keyword2',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='keyword3',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='keyword4',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='keyword5',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='keyword6',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='templatemessagetemplate',
            name='remark',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]

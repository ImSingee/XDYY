# Generated by Django 2.0.3 on 2018-06-15 23:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('wechat', '0004_auto_20180615_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateMessageTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(
                    choices=[(-1, '未定义'), (201, 'TO预约人 - 预约提交成功'), (202, 'TO预约人 - 预约被拒绝'), (203, 'TO预约人 - 预约被取消'),
                             (204, 'TO预约人 - 预约被确认'), (205, 'TO预约人 - 预约已完成'), (206, 'TO预约人 - 预约被标记为无故不出席'),
                             (211, 'TO预约人 - 预约即将开始提醒'), (301, 'TO被预约人 - 收到预约'), (302, 'TO被预约人 - 预约未即时确认提醒'),
                             (303, 'TO被预约人 - 预约超时取消提醒'), (304, 'TO被预约人 - 预约完成提醒'), (311, 'TO被预约人 - 预约即将开始提醒')],
                    verbose_name='类别')),
                ('first', models.CharField(blank=True, default='', max_length=1024)),
                ('keyword1', models.CharField(blank=True, default='', max_length=1024)),
                ('keyword2', models.CharField(blank=True, default='', max_length=1024)),
                ('keyword3', models.CharField(blank=True, default='', max_length=1024)),
                ('keyword4', models.CharField(blank=True, default='', max_length=1024)),
                ('keyword5', models.CharField(blank=True, default='', max_length=1024)),
                ('keyword6', models.CharField(blank=True, default='', max_length=1024)),
                ('remark', models.CharField(blank=True, default='', max_length=1024)),
                ('url', models.CharField(blank=True, default='', max_length=1024)),
            ],
            options={
                'verbose_name': '模板消息触发器',
                'verbose_name_plural': '模板消息触发器',
            },
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='first',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='keyword1',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='keyword2',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='keyword3',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='keyword4',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='keyword5',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='keyword6',
        ),
        migrations.RemoveField(
            model_name='templatemessagetemplate',
            name='remark',
        ),
        migrations.AddField(
            model_name='templatemessagetrigger',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='wechat.TemplateMessageTemplate'),
        ),
    ]

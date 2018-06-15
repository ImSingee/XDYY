# Generated by Django 2.0.3 on 2018-06-15 19:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reserve', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reserverecord',
            options={'permissions': (
            ('new', '预约他人'), ('confirm', '确认预约'), ('reject_reserverecord', '拒绝预约'), ('cancel_reserverecord', '取消预约')),
                     'verbose_name': '预约记录', 'verbose_name_plural': '预约记录'},
        ),
        migrations.AlterField(
            model_name='reserverecord',
            name='status',
            field=models.IntegerField(
                choices=[(-201, '预约人未出席'), (-101, '预约人取消预约'), (-102, '被预约人取消预约'), (-105, '被预约人拒绝预约'), (-103, '管理员取消预约'),
                         (-104, '被预约人超时未答复自动取消预约'), (0, '预约已提交'), (100, '预约已确认'), (200, '预约已完成')], default=0,
                verbose_name='状态'),
        ),
    ]

# Generated by Django 2.0.3 on 2018-06-16 00:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('wechat', '0006_templatemessagetrigger_mini_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='first',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='keyword1',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='keyword2',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='keyword3',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='keyword4',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='keyword5',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='keyword6',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='templatemessagetrigger',
            name='remark',
            field=models.TextField(blank=True, default=''),
        ),
    ]

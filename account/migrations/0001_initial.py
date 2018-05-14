# Generated by Django 2.0.3 on 2018-03-19 17:16

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=50, verbose_name='姓名')),
                ('gender', models.IntegerField(choices=[(-1, '未知'), (1, '男'), (2, '女')], default=-1, verbose_name='性别')),
                ('tel', models.CharField(blank=True, default='', max_length=60, verbose_name='电话号码')),
                ('id_card_no', models.CharField(blank=True, default='', max_length=80, verbose_name='身份证号')),
                ('avatar', models.ImageField(default='default/default.png', height_field='avatar_height', upload_to='avatars/', verbose_name='头像', width_field='avatar_width')),
                ('avatar_height', models.PositiveIntegerField(blank=True, default='120', editable=False, null=True, verbose_name='头像高度')),
                ('avatar_width', models.PositiveIntegerField(blank=True, default='120', editable=False, null=True, verbose_name='头像宽度')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserver', models.BooleanField(default=False, verbose_name='预约人')),
                ('reservee', models.BooleanField(default=False, verbose_name='被预约人')),
                ('auth_code', models.CharField(blank=True, max_length=80, null=True, verbose_name='预约人编码')),
                ('auth_name', models.CharField(blank=True, max_length=80, null=True, verbose_name='预约人姓名')),
                ('can_reserved', models.BooleanField(default=False, verbose_name='可被预约')),
                ('short_intro', models.TextField(blank=True, null=True, verbose_name='简介')),
                ('intro', models.TextField(blank=True, null=True, verbose_name='介绍')),
                ('default_address', models.CharField(blank=True, max_length=160, null=True, verbose_name='默认地点')),
                ('zhuanye', models.CharField(blank=True, default='', max_length=80, verbose_name='专业')),
                ('banji', models.CharField(blank=True, default='', max_length=80, verbose_name='班级')),
            ],
            options={
                'verbose_name': '用户额外信息',
                'verbose_name_plural': '用户额外信息',
            },
        ),
    ]
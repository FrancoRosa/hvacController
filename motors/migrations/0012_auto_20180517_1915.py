# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-05-17 19:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motors', '0011_auto_20180516_0205'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='administrator',
            options={'verbose_name_plural': 'Administradores'},
        ),
        migrations.AlterModelOptions(
            name='alert',
            options={'verbose_name_plural': 'Alertas'},
        ),
        migrations.AlterModelOptions(
            name='building',
            options={'verbose_name_plural': 'Edificios'},
        ),
        migrations.AlterModelOptions(
            name='cooler',
            options={'verbose_name_plural': 'HVAC'},
        ),
        migrations.AlterModelOptions(
            name='floor',
            options={'verbose_name_plural': 'Pisos'},
        ),
        migrations.AlterModelOptions(
            name='schedule',
            options={'verbose_name_plural': 'Horarios'},
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='begin',
            new_name='s_start',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='end',
            new_name='s_stop',
        ),
        migrations.AlterField(
            model_name='schedule',
            name='day',
            field=models.CharField(choices=[('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'), ('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday'), ('0', 'Sunday')], max_length=1),
        ),
    ]

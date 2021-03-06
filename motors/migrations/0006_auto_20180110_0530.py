# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-10 05:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motors', '0005_auto_20180110_0513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='floor_name',
            field=models.CharField(default='Sotano', max_length=25),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_name',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='status',
            name='temperature',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]

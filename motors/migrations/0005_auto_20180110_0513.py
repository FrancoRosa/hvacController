# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-10 05:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motors', '0004_room_modbus_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='floor_name',
            field=models.CharField(default='Sotano', max_length=20),
        ),
    ]
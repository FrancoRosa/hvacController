# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-10 04:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motors', '0002_auto_20180110_0453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='temperature',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]

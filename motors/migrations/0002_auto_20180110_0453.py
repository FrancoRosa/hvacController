# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-10 04:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('motors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=20)),
                ('floor_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel_1', models.CharField(choices=[('ON', 'On'), ('OFF', 'Off')], default='OFF', max_length=3)),
                ('nivel_2', models.CharField(choices=[('ON', 'On'), ('OFF', 'Off')], default='OFF', max_length=3)),
                ('nivel_3', models.CharField(choices=[('ON', 'On'), ('OFF', 'Off')], default='OFF', max_length=3)),
                ('light', models.CharField(choices=[('ON', 'On'), ('OFF', 'Off')], default='OFF', max_length=3)),
                ('temperature', models.DecimalField(decimal_places=1, max_digits=2)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='motors.Room')),
            ],
        ),
        migrations.DeleteModel(
            name='Rooms',
        ),
    ]

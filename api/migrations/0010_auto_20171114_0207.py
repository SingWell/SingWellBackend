# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-14 02:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20171114_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choir',
            name='meeting_day_end_hour',
            field=models.TimeField(null=True),
        ),
    ]

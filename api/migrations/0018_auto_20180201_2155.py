# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-01 21:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20180130_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(null=True),
        ),
    ]
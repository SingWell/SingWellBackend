# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-13 21:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20171113_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choir',
            name='choristers',
            field=models.ManyToManyField(related_name='in_choirs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='choir',
            name='perform_day',
            field=models.IntegerField(blank=True, choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], null=True),
        ),
        migrations.AlterField(
            model_name='choir',
            name='perform_day_start_hour',
            field=models.TimeField(null=True),
        ),
    ]

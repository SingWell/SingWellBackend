# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-28 22:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20171128_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='choir',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
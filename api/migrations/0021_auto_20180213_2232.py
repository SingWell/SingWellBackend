# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-13 22:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20180202_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='email',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='phone_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='choir',
            name='choristers',
            field=models.ManyToManyField(related_name='choirs', to=settings.AUTH_USER_MODEL),
        ),
    ]

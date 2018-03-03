# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-27 22:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20180220_1620'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='programmed_music',
        ),
        migrations.AddField(
            model_name='programfield',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Event'),
        ),
        migrations.AddField(
            model_name='programfield',
            name='music_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.MusicRecord'),
        ),
        migrations.AddField(
            model_name='event',
            name='program_music',
            field=models.ManyToManyField(through='api.ProgramField', to='api.MusicRecord'),
        ),
    ]
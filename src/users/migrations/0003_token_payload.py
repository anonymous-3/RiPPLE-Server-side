# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-19 23:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20170920_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='payload',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
    ]

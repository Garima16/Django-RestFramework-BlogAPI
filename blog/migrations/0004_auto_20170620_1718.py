# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-20 17:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20170612_0922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 20, 17, 18, 34, 784960, tzinfo=utc)),
        ),
    ]

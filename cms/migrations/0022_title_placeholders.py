# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-02 16:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0021_auto_20180507_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='placeholders',
            field=models.ManyToManyField(editable=False, to='cms.Placeholder'),
        ),
    ]

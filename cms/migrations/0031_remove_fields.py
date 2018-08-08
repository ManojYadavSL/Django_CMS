# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-10 15:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0030_auto_20180810_0629'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='page',
            name='publisher_public',
        ),
        migrations.RemoveField(
            model_name='page',
            name='publisher_is_draft',
        ),
        migrations.RemoveField(
            model_name='page',
            name='publication_date',
        ),
        migrations.RemoveField(
            model_name='page',
            name='publication_end_date',
        ),
        migrations.RemoveField(
            model_name='page',
            name='template',
        ),
        migrations.RemoveField(
            model_name='page',
            name='xframe_options',
        ),
        migrations.RemoveField(
            model_name='page',
            name='in_navigation',
        ),
        migrations.RemoveField(
            model_name='page',
            name='soft_root',
        ),
        migrations.RemoveField(
            model_name='page',
            name='limit_visibility_in_menu',
        ),
        migrations.RemoveField(
            model_name='title',
            name='publisher_is_draft',
        ),
        migrations.RemoveField(
            model_name='title',
            name='publisher_public',
        ),
        migrations.RemoveField(
            model_name='title',
            name='published',
        ),
        migrations.RemoveField(
            model_name='title',
            name='publisher_state',
        ),
        migrations.RemoveField(
            model_name='title',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='title',
            name='path',
        ),
        migrations.RemoveField(
            model_name='title',
            name='has_url_overwrite',
        ),
    ]

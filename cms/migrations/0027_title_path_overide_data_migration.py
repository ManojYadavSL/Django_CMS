# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-18 16:06
from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    """
    Move all title paths from titles with has_url_overwrite set to True and then remove path field.
    """
    Title = apps.get_model('cms', 'Title')
    db_alias = schema_editor.connection.alias

    title_list = (
        Title
        .objects
        .using(db_alias)
        .filter(has_path_override__isnull=True)
        .distinct()
    )

    for title in title_list:
        title.path_override = title.path
        title.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0026_auto_20180718_1606'),
    ]

    operations = [
        migrations.RunPython(forwards)
    ]

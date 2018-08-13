# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-08 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0028_remove_page_placeholders'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='changed_by',
            field=models.CharField(editable=False, max_length=255, null=True, verbose_name='changed by'),
        ),
        migrations.AddField(
            model_name='title',
            name='changed_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='title',
            name='created_by',
            field=models.CharField(editable=False, max_length=255, null=True, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='title',
            name='in_navigation',
            field=models.BooleanField(db_index=True, default=True, verbose_name='in navigation'),
        ),
        migrations.AddField(
            model_name='title',
            name='limit_visibility_in_menu',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'for logged in users only'), (2, 'for anonymous users only')], db_index=True, default=None, help_text='limit when this page is visible in the menu', null=True, verbose_name='menu visibility'),
        ),
        migrations.AddField(
            model_name='title',
            name='template',
            field=models.CharField(choices=[('col_two.html', 'two columns'), ('col_three.html', 'three columns'), ('nav_playground.html', 'navigation examples'), ('simple.html', 'simple'), ('static.html', 'static placeholders'), ('INHERIT', 'Inherit the template of the nearest ancestor')], default='INHERIT', help_text='The template used to render the content.', max_length=100, verbose_name='template'),
        ),
        migrations.AddField(
            model_name='title',
            name='xframe_options',
            field=models.IntegerField(choices=[(0, 'Inherit from parent page'), (1, 'Deny'), (2, 'Only this website'), (3, 'Allow')], default=0),
        ),
        migrations.AddField(
            model_name='title',
            name='soft_root',
            field=models.BooleanField(db_index=True, default=False, help_text='All ancestors will not be displayed in the navigation', verbose_name='soft root'),
        ),
    ]

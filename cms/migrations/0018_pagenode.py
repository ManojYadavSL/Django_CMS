# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-07 17:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def get_descendants(root):
    """
    Returns the a generator of primary keys which represent
    descendants of the given page ID (root_id)
    """
    # Note this is done because get_descendants() can't be trusted
    # as the tree can be corrupt.

    for child in root.children.order_by('path').iterator():
        yield child

        for child in get_descendants(child):
            yield child


def migrate_to_page_nodes(apps, schema_editor):
    Page = apps.get_model('cms', 'Page')
    PageNode = apps.get_model('cms', 'PageNode')
    db_alias = schema_editor.connection.alias

    root_draft_pages = Page.objects.using(db_alias).filter(
        publisher_is_draft=True,
        parent__isnull=True,
    )

    create_node = PageNode.objects.using(db_alias).create

    nodes_by_page = {}

    for root in root_draft_pages:
        page_node = create_node(
            page=root,
            site_id=root.site_id,
            path=root.path,
            depth=root.depth,
            numchild=root.numchild,
            parent=None
        )
        nodes_by_page[root.pk] = page_node

        for descendant in get_descendants(root):
            descendant_node = create_node(
                page=descendant,
                site_id=descendant.site_id,
                path=descendant.path,
                depth=descendant.depth,
                numchild=descendant.numchild,
                parent=nodes_by_page[descendant.parent_id],
            )
            nodes_by_page[descendant.pk] = descendant_node


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0017_pagetype'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_page_type',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='PageNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Page', related_name='nodes')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cms.PageNode')),
                ('site', models.ForeignKey(help_text='The site the page is accessible at.', on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_page_nodes', to='sites.Site', verbose_name='site')),
            ],
            options={
                'ordering': ('path',),
                'default_permissions': (),
            },
        ),
        migrations.AlterUniqueTogether(
            name='pagenode',
            unique_together=set([('page', 'site')]),
        ),
        migrations.RunPython(migrate_to_page_nodes),
        migrations.RemoveField(
            model_name='page',
            name='depth',
        ),
        migrations.RemoveField(
            model_name='page',
            name='numchild',
        ),
        migrations.RemoveField(
            model_name='page',
            name='path',
        ),
        migrations.RemoveField(
            model_name='page',
            name='parent',
        ),
    ]

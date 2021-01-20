from django.db import migrations

from . import IrreversibleMigration


def unpublish_never_published_pages(apps, schema_editor):
    """
    Prior to 3.5, pages would be marked as "pending"
    when users tried to publish a page with an unpublished parent.
    This is no longer allowed, as a result any page that's set as
    published but does not have a public version is marked as unpublished.
    """
    Page = apps.get_model('cms', 'Page')
    db_alias = schema_editor.connection.alias
    draft_pages = Page.objects.using(db_alias).filter(publisher_is_draft=True)
    never_published_pages = Page.objects.using(db_alias).filter(
        title_set__published=True,
        publisher_is_draft=True,
        publisher_public__isnull=True,
    )

    for page in never_published_pages.distinct():
        page.title_set.update(
            published=False,
            publisher_state=1,
        )
        draft_pages.filter(pk=page.pk).update(
            publication_date=None,
            publication_end_date=None,
        )


def set_page_nodes(apps, schema_editor):
    Page = apps.get_model('cms', 'Page')
    TreeNode = apps.get_model('cms', 'TreeNode')
    db_alias = schema_editor.connection.alias
    draft_pages = Page.objects.using(db_alias).filter(publisher_is_draft=True)
    public_pages = Page.objects.using(db_alias).filter(publisher_is_draft=False)
    nodes_by_path = {node.path: node for node in TreeNode.objects.all()}

    for draft_page in draft_pages:
        draft_page.node = nodes_by_path[draft_page.path]
        draft_page.save(update_fields=['node'])

        if draft_page.publisher_public_id:
            public_pages.filter(pk=draft_page.publisher_public_id).update(node=draft_page.node)


class Migration(IrreversibleMigration):

    dependencies = [
        ('cms', '0018_create_pagenode'),
    ]

    operations = [
        migrations.RunPython(unpublish_never_published_pages, migrations.RunPython.noop),
        migrations.RunPython(set_page_nodes, migrations.RunPython.noop),
    ]

    def apply(self, project_state, schema_editor, collect_sql=False):
        connection = schema_editor.connection
        column_names = [
            column.name for column in
            connection.introspection.get_table_description(connection.cursor(), 'cms_page')
        ]

        if 'migration_0018_control' in column_names:
            # The new 0018 migration has been applied
            return super().apply(project_state, schema_editor, collect_sql)

        # The old 0018 migration was applied
        # Move the project state forward without actually running
        # any of the operations against the database.
        for operation in self.operations:
            operation.state_forwards(self.app_label, project_state)
        return project_state

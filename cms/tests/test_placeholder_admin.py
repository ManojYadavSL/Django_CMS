# -*- coding: utf-8 -*-
from django.forms.models import model_to_dict

from cms.api import add_plugin
from cms.models import Placeholder, UserSettings, CMSPlugin
from cms.test_utils.testcases import CMSTestCase


class PlaceholderAdminTestCase(CMSTestCase):

    # FIXME: Should be a reusable method in testcase!
    def _add_plugin_to_placeholder(self, placeholder, plugin_type='LinkPlugin', language='en'):
        plugin_data = {
            'TextPlugin': {'body': '<p>text</p>'},
            'LinkPlugin': {'name': 'A Link', 'external_link': 'https://www.django-cms.org'},
        }
        plugin = add_plugin(placeholder, plugin_type, language, **plugin_data[plugin_type])
        return plugin

    def test_add_plugin_endpoint(self):
        """
        The Placeholder admin add_plugin endpoint works
        """
        superuser = self.get_superuser()
        placeholder = Placeholder.objects.create(slot='test')
        plugins = placeholder.get_plugins('en').filter(plugin_type='LinkPlugin')
        uri = self.get_add_plugin_uri(
            placeholder=placeholder,
            plugin_type='LinkPlugin',
            language='en',
        )
        with self.login_user_context(superuser):
            data = {'name': 'A Link', 'external_link': 'https://www.django-cms.org'}
            response = self.client.post(uri, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(plugins.count(), 1)

    def test_copy_plugins_add_plugins_from_placeholder(self):
        """
        User can copy plugins from one placeholder to another
        """
        superuser = self.get_superuser()
        source_placeholder = Placeholder.objects.create(slot='source')
        target_placeholder = Placeholder.objects.create(slot='target')
        source_plugin = self._add_plugin_to_placeholder(source_placeholder)
        endpoint = self.get_copy_plugin_uri(source_plugin)
        with self.login_user_context(superuser):
            data = {
                'source_language': "en",
                'source_placeholder_id': source_placeholder.pk,
                'target_language': "en",
                'target_placeholder_id': target_placeholder.pk,
            }
            response = self.client.post(endpoint, data)

        # Test that the target placeholder has the plugin copied from the source placeholder
        self.assertEqual(response.status_code, 200)
        self.assertTrue(source_placeholder.get_plugins('en').filter(pk=source_plugin.pk).exists())
        self.assertTrue(
            target_placeholder
                .get_plugins('en')
                .filter(plugin_type=source_plugin.plugin_type)
                .exists()
        )

    def test_copy_plugins_copy_plugin_to_clipboard(self):
        """
        User can copy plugins from a placeholder to the clipboard
        """
        superuser = self.get_superuser()
        user_settings = UserSettings.objects.create(
            language="en",
            user=superuser,
            clipboard=Placeholder.objects.create(),
        )
        source_placeholder = Placeholder.objects.create(slot='source')
        source_plugin = self._add_plugin_to_placeholder(source_placeholder)
        endpoint = self.get_copy_plugin_uri(source_plugin)
        with self.login_user_context(superuser):
            data = {
                'source_language': "en",
                'source_placeholder_id': source_placeholder.pk,
                'source_plugin_id': source_plugin.pk,
                'target_language': "en",
                'target_placeholder_id': user_settings.clipboard.pk,
            }
            response = self.client.post(endpoint, data)

        # Test that the target placeholder has the plugin copied from the source placeholder (clipboard)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(source_placeholder.get_plugins('en').filter(pk=source_plugin.pk).exists())
        self.assertTrue(
            user_settings.clipboard
                .get_plugins('en')
                .filter(plugin_type=source_plugin.plugin_type)
                .exists()
        )

    def test_copy_plugins_copy_placeholder_to_clipboard(self):
        """
        User can copy a placeholder to the clipboard
        """
        superuser = self.get_superuser()
        user_settings = UserSettings.objects.create(
            language="en",
            user=superuser,
            clipboard=Placeholder.objects.create(),
        )
        source_placeholder = Placeholder.objects.create(slot='source')
        source_plugin = self._add_plugin_to_placeholder(source_placeholder)
        endpoint = self.get_copy_plugin_uri(source_plugin)
        with self.login_user_context(superuser):
            data = {
                'source_language': "en",
                'source_placeholder_id': source_placeholder.pk,
                'target_language': "en",
                'target_placeholder_id': user_settings.clipboard.pk,
            }
            response = self.client.post(endpoint, data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(source_placeholder.get_plugins('en').filter(pk=source_plugin.pk).exists())
        self.assertTrue(
            user_settings.clipboard
                .get_plugins('en')
                .filter(plugin_type='PlaceholderPlugin')
                .exists()
        )

    def test_edit_plugin_endpoint(self):
        """
        The Placeholder admin edit_plugins endpoint works
        """
        superuser = self.get_superuser()
        placeholder = Placeholder.objects.create(slot='edit_plugin_placeholder')
        plugin = self._add_plugin_to_placeholder(placeholder)
        endpoint = self.get_admin_url(Placeholder, 'edit_plugin', plugin.pk)
        with self.login_user_context(superuser):
            data = model_to_dict(plugin, fields=['name', 'external_link'])
            data['name'] = 'Contents modified'
            response = self.client.post(endpoint, data)
            plugin.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(plugin.name, data['name'])

    def test_move_plugin_endpoint(self):
        """
        The Placeholder admin move_plugin endpoint works

        TODO: Test??
            - _paste_placeholder
            - _paste_plugin
            - _cut_plugin
            - _move_plugin
        """
        superuser = self.get_superuser()
        source_placeholder = Placeholder.objects.create(slot='source')
        target_placeholder = Placeholder.objects.create(slot='target')
        plugin = self._add_plugin_to_placeholder(source_placeholder)
        endpoint = self.get_admin_url(Placeholder, 'move_plugin')
        with self.login_user_context(superuser):
            data = {
                'plugin_id': plugin.pk,
                'target_language': 'en',
                'placeholder_id': target_placeholder.pk,
                'target_position': target_placeholder.get_next_plugin_position('en', insert_order='last'),
            }
            response = self.client.post(endpoint, data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(target_placeholder.get_plugins('en').filter(pk=plugin.pk))
        self.assertFalse(source_placeholder.get_plugins('en').filter(pk=plugin.pk))

    def test_delete_plugin_endpoint(self):
        """
        The Placeholder admin delete_plugin endpoint works
        """
        superuser = self.get_superuser()
        placeholder = Placeholder.objects.create(slot='source')
        plugin = self._add_plugin_to_placeholder(placeholder)
        endpoint = self.get_admin_url(Placeholder, 'delete_plugin', plugin.pk)
        with self.login_user_context(superuser):
            data = {'post': True}
            response = self.client.post(endpoint, data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(CMSPlugin.objects.filter(pk=plugin.pk).exists())

    def test_clear_placeholder_endpoint(self):
        """
        The Placeholder admin delete_plugin endpoint works
        """
        superuser = self.get_superuser()
        placeholder = Placeholder.objects.create(slot='source')
        self._add_plugin_to_placeholder(placeholder)
        endpoint = self.get_admin_url(Placeholder, 'clear_placeholder', placeholder.pk)
        with self.login_user_context(superuser):
            response = self.client.post(endpoint, {'test': 0})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(placeholder.get_plugins('en').count(), 0)
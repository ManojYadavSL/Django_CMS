# -*- coding: utf-8 -*-
from cms.utils.compat.dj import python_2_unicode_compatible
from cms.utils.helpers import reversion_register
from cms.utils.placeholder import PlaceholderNoAction
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.widgets import Media
from django.utils.translation import ugettext_lazy as _
import operator


@python_2_unicode_compatible
class Placeholder(models.Model):
    slot = models.CharField(_("slot"), max_length=50, db_index=True, editable=False)
    default_width = models.PositiveSmallIntegerField(_("width"), null=True, editable=False)

    class Meta:
        app_label = 'cms'

    def __str__(self):
        return self.slot

    def get_add_url(self):
        return self._get_url('add_plugin')

    def get_move_url(self):
        return self._get_url('move_plugin')

    def get_remove_url(self):
        return self._get_url('remove_plugin')

    def get_changelist_url(self):
        return self._get_url('changelist')

    def _get_url(self, key):
        model = self._get_attached_model()
        if not model:
            return reverse('admin:cms_page_%s' % key)
        else:
            app_label = model._meta.app_label
            model_name = model.__name__.lower()
            return reverse('admin:%s_%s_%s' % (app_label, model_name, key))

    def _get_permission(self, request, key):
        """
        Generic method to check the permissions for a request for a given key,
        the key can be: 'add', 'change' or 'delete'. For each attached object
        permission has to be granted either on attached model or on attached object.
        """
        if request.user.is_superuser:
            return True
        found = False
        # check all attached models/objects for change permissions
        for object in self._get_attached_objects():
            model = object.__class__
            opts = model._meta
            perm_accessor = getattr(opts, 'get_%s_permission' % key)
            perm_code = '%s.%s' % (opts.app_label, perm_accessor())
            # if they don't have the permission for this attached model or object, bail out
            if not (request.user.has_perm(perm_code) or request.user.has_perm(perm_code, object)):
                return False
            else:
                found = True
        return found

    def has_change_permission(self, request):
        return self._get_permission(request, 'change')

    def has_add_permission(self, request):
        return self._get_permission(request, 'add')

    def has_delete_permission(self, request):
        return self._get_permission(request, 'delete')

    def render(self, context, width, lang=None):
        from cms.plugin_rendering import render_placeholder
        if not 'request' in context:
            return '<!-- missing request -->'
        width = width or self.default_width
        if width:
            context.update({'width': width})
        return render_placeholder(self, context, lang=lang)

    def get_media(self, request, context):
        from cms.plugins.utils import get_plugin_media
        media_classes = [get_plugin_media(request, context, plugin) for plugin in self.get_plugins()]
        if media_classes:
            return reduce(operator.add, media_classes)
        return Media()

    def _get_attached_fields(self):
        """
        Returns an ITERATOR of all non-cmsplugin reverse foreign key related fields.
        """
        from cms.models import CMSPlugin
        for rel in self._meta.get_all_related_objects():
            if issubclass(rel.model, CMSPlugin):
                continue
            field = getattr(self, rel.get_accessor_name())
            if field.count():
                yield rel.field

    def _get_attached_field(self):
        from cms.models import CMSPlugin
        if not hasattr(self, '_attached_field_cache'):
            self._attached_field_cache = None
            for rel in self._meta.get_all_related_objects():
                if issubclass(rel.model, CMSPlugin):
                    continue
                field = getattr(self, rel.get_accessor_name())
                if field.count():
                    self._attached_field_cache = rel.field
        return self._attached_field_cache

    def _get_attached_field_name(self):
        field = self._get_attached_field()
        if field:
            return field.name
        return None

    def _get_attached_model(self):
        field = self._get_attached_field()
        if field:
            return field.model
        return None

    def _get_attached_models(self):
        """
        Returns a list of models of attached to this placeholder.
        """
        return [field.model for field in self._get_attached_fields()]

    def _get_attached_objects(self):
        """
        Returns a list of objects attached to this placeholder.
        """
        return [obj for field in self._get_attached_fields()
                for obj in getattr(self, field.related.get_accessor_name()).all()]

    def page_getter(self):
        if not hasattr(self, '_page'):
            from cms.models.pagemodel import Page
            try:
                self._page = Page.objects.get(placeholders=self)
            except (Page.DoesNotExist, Page.MultipleObjectsReturned,):
                self._page = None
        return self._page

    def page_setter(self, value):
        self._page = value

    page = property(page_getter, page_setter)

    def get_plugins_list(self, language=None):
        return list(self.get_plugins(language))

    def get_plugins(self, language=None):
        if language:
            return self.cmsplugin_set.filter(language=language).order_by('tree_id', 'lft')
        else:
            return self.cmsplugin_set.all().order_by('tree_id', 'lft')

    @property
    def actions(self):
        if not hasattr(self, '_actions_cache'):
            field = self._get_attached_field()
            self._actions_cache = getattr(field, 'actions', PlaceholderNoAction())
        return self._actions_cache

reversion_register(Placeholder)  # follow=["cmsplugin_set"] not following plugins since they are a spechial case

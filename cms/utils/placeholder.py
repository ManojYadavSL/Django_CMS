# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db.models.query_utils import Q

def get_placeholder_conf(setting, placeholder, template=None, default=None):
    """
    Returns the placeholder configuration for a given setting. The key would for
    example be 'plugins'  or 'name'.
    
    If a template is given, it will try
    CMS_PLACEHOLDER_CONF['template placeholder'] and
    CMS_PLACEHOLDER_CONF['placeholder'], if no template is given only the latter
    is checked.
    """
    keys = []
    if template:
        keys.append("%s %s" % (template, placeholder))
    keys.append(placeholder)
    for key in keys:
        conf = settings.CMS_PLACEHOLDER_CONF.get(key)
        if not conf:
            continue
        value = conf.get(setting)
        if value:
            return value
    return default

def get_page_from_placeholder_if_exists(placeholder):
    from cms.models.pagemodel import Page
    try:
        return Page.objects.get(placeholders=placeholder)
    except (Page.DoesNotExist, MultipleObjectsReturned,):
        return None
    
class PlaceholderNoAction(object):
    can_copy = False
    
    def copy(self, **kwargs):
        return False
    
    def get_copy_languages(self, **kwargs):
        return []
    
    
class MLNGPlaceholderActions(PlaceholderNoAction):
    can_copy = True

    def copy(self, target_placeholder, source_language, fieldname, model, target_language, **kwargs):
        trgt = model.objects.get(**{fieldname: target_placeholder})
        src = model.objects.get(master=trgt.master, language_code=source_language)

        source_placeholder = getattr(src, fieldname, None)
        if not source_placeholder:
            return False
        plugins = source_placeholder.get_plugins_list()
        ptree = []
        new_plugins = []
        for p in plugins:
            new_plugins.append(p.copy_plugin(target_placeholder, target_language, ptree))
        return new_plugins
    
    def get_copy_languages(self, placeholder, model, fieldname, **kwargs):
        manager = model.objects
        src = manager.get(**{fieldname: placeholder})
        q = Q(master=src.master)
        q &= Q(**{'%s__cmsplugin__isnull' % fieldname: False})
        q &= ~Q(pk=src.pk)
        
        language_codes = manager.filter(q).values_list('language_code', flat=True).distinct()
        return [(lc, dict(settings.LANGUAGES)[lc]) for lc in language_codes]
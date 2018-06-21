from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from cms.utils.compat.dj import is_installed as app_is_installed
from cms.app_registration import (
    autodiscover_cms_configs, get_cms_apps_with_features,
    configure_cms_apps)


def validate_dependencies():
    """
    Check for installed apps, their versions and configuration options
    """
    if not app_is_installed('treebeard'):
        raise ImproperlyConfigured('django CMS requires django-treebeard. Please install it and add "treebeard" to INSTALLED_APPS.')


def validate_settings():
    """
    Check project settings file for required options
    """
    try:
        django_backend = [x for x in settings.TEMPLATES
                          if x['BACKEND'] == 'django.template.backends.django.DjangoTemplates'][0]
    except IndexError:
        raise ImproperlyConfigured("django CMS requires django.template.context_processors.request in "
                                   "'django.template.backends.django.DjangoTemplates' context processors.")

    context_processors = django_backend.get('OPTIONS', {}).get('context_processors', [])
    if ('django.core.context_processors.request' not in context_processors and
            'django.template.context_processors.request' not in context_processors):
        raise ImproperlyConfigured("django CMS requires django.template.context_processors.request in "
                                   "'django.template.backends.django.DjangoTemplates' context processors.")


def setup():
    """
    Gather all checks and validations
    """
    from cms.plugin_pool import plugin_pool
    validate_dependencies()
    validate_settings()
    plugin_pool.validate_templates()


def setup_cms_apps():
    """
    Check for django apps which provide functionality that extends the
    cms. Configure all apps which have configs that declare use of
    any of this functionality.
    """
    autodiscover_cms_configs()
    apps_with_cms_features = get_cms_apps_with_features()
    configure_cms_apps(apps_with_cms_features)

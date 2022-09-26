import json

from django import template
from django.utils.safestring import mark_safe

from cms.utils.encoder import SafeJSONEncoder
from cms.utils.placeholder import get_declared_placeholders_for_obj, rescan_placeholders_for_obj

from classytags.core import Tag, Options

from sekizai.helpers import get_varname


register = template.Library()


@register.filter('json')
def json_filter(value):
    """
    Returns the JSON representation of ``value`` in a safe manner.
    """
    return mark_safe(json.dumps(value, cls=SafeJSONEncoder))


@register.filter
def bool(value):
    if value:
        return 'true'
    else:
        return 'false'


@register.simple_tag()
def render_cms_structure_js(renderer, obj):
    markup_bits = []
    obj_placeholders_by_slot = rescan_placeholders_for_obj(obj)
    declared_placeholders = get_declared_placeholders_for_obj(obj)

    for placeholder_node in declared_placeholders:
        obj_placeholder = obj_placeholders_by_slot.get(placeholder_node.slot)

        if obj_placeholder:
            placeholder_js = renderer.render_placeholder(obj_placeholder, language=None, page=obj)
            markup_bits.append(placeholder_js)

    return mark_safe('\n'.join(markup_bits))


@register.simple_tag(takes_context=True)
def render_plugin_init_js(context, plugin):
    renderer = context['cms_renderer']
    plugin_js = renderer.get_plugin_toolbar_js(plugin)
    # Add the toolbar javascript for this plugin to the
    # sekizai "js" namespace.
    context[get_varname()]['js'].append('<script data-cms>{}</script>'.format(plugin_js))


@register.tag(name="javascript_string")
class JavascriptString(Tag):
    name = 'javascript_string'
    options = Options(
        blocks=[
            ('end_javascript_string', 'nodelist'),
        ]
    )

    def render_tag(self, context, **kwargs):
        try:
            from django.utils.html import escapejs
        except ImportError:
            from django.utils.text import javascript_quote as escapejs
        rendered = self.nodelist.render(context)
        return "'%s'" % escapejs(rendered.strip())

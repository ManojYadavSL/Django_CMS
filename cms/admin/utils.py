from urllib.parse import parse_qsl

from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import NoReverseMatch
from django.utils.html import format_html_join
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext_lazy as _

from cms.toolbar.utils import get_object_preview_url
from cms.utils import get_language_from_request
from cms.utils.i18n import get_language_dict, get_language_tuple
from cms.utils.urlutils import admin_reverse, static_with_version


class ChangeListActionsMixin(metaclass=forms.MediaDefiningClass):
    """AdminListActionsMixin is a mixin for the ModelAdmin class. It adds the ability to have
     action buttons and a burger menu in the admin's change list view. Unlike actions that affect
     multiple listed items the list action buttons only affect one item at a time.

     Use :meth:`~cms.admin.utils.AdminListActionsMixin.get_action_list` to register actions and
     :meth:`~cms.admin.utils.AdminListActionsMixin.admin_action_button` to define the button
     behavior.

     To activate the actions make sure ``"admin_list_actions"`` is in the admin classes
     :prop:`~django.contrib.admin.ModelAdmin.list_display` property.
     """

    class Media:
        js = (
            "admin/js/jquery.init.js",
            "cms/js/admin/actions.js",
        )
        css = {"all": (
            static_with_version("cms/css/cms.admin.css"),
        )}

    def get_actions_list(self):
        """Collect list actions from implemented methods and return as list. Make sure to call
        it's ``super()`` instance when overwriting::

            class MyModelAdmin(admin.ModelAdmin):
                ...

                def get_actions_list(self):
                    return super().get_actions_list() + [self.my_first_action, self.my_second_action]
        """
        return []

    def get_admin_list_actions(self, request):
        """Method to register the admin action menu with the admin's list display

        Usage (in your model admin)::

            class MyModelAdmin(AdminActionsMixin, admin.ModelAdmin):
                ...
                list_display = ('name', ..., 'admin_list_actions')

        """
        def list_actions(obj):
            """The name of this inner function must not change. css styling and js depends on it."""
            EMPTY = mark_safe('<span class="cms-empty-action"></span>')
            return format_html_join(
                "",
                "{}",
                ((action(obj, request) or EMPTY,) for action in self.get_actions_list()),
            )

        list_actions.short_description = _("Actions")
        return list_actions

    def admin_list_actions(self, obj):
        raise ValueError(
            "ModelAdmin.display_list contains \"admin_list_actions\" as a placeholder for list action icons. "
            "AdminListActionsMixin is not loaded, however. If you implement \"get_list_display\" make "
            "sure it calls super().get_list_display."
        )  # pragma: no cover

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return tuple(self.get_admin_list_actions(request) if item == "admin_list_actions" else item
                     for item in list_display)

    @staticmethod
    def admin_action_button(
        url,
        icon,
        title,
        burger_menu=False,
        action="get",
        disabled=False,
        keepsideframe=True,
        name="",
    ):
        """Returns a generic button supported by the AdminListActionsMixin.

        :param str url:  Url of the action as string, typically generated by :func:`~cms.utils.urlutils.admin_reverse`_
        :param str icon: Name of the icon shown in the button or before the title in the burger menu.
        :param str title: Human-readable string describing the action.
        :param bool burger_menu: If ``True`` the action item will be part of a burger menu right og all buttons.
        :param str action: Either ``"get"`` or ``"post"`` defining the html method used for the url. Some urls
                           require a post method.
        :param bool disabled: If ``True`` the item is grayed out and cannot be selected.
        :param bool keepsideframe:  If ``False`` the side frame (if open) will be closed before execcuting the action.
        :param str name: A string that will be added to the class list of the button/menu item:
                         ``cms-action-{{ name }}``

        To add an action button to the change list use the following pattern in your admin class::

                 def my_custom_button(self, obj, request, disabled=False):
                    # do preparations, e.g., check permissions, get url, ...
                    url = admin_reverse("...", args=[obj.pk])
                    if permissions_ok:
                        return self.admin_action_button(url, "info",  _("View usage"), disabled=disabled)
                    return ""  # No button

        """
        return render_to_string(
            "admin/cms/icons/base.html",
            {
                "url": url or "",
                "icon": icon,
                "action": action,
                "disabled": disabled,
                "keepsideframe": keepsideframe,
                "title": title,
                "burger_menu": burger_menu,
                "name": name,
            }
        )


class GrouperChangeListBase(ChangeList):
    """Subclass ChangeList to disregard language get parameter as filter"""
    _extra_grouping_fields = []

    def get_filters_params(self, params=None):
        lookup_params = super().get_filters_params(params)
        for field in self._extra_grouping_fields:
            if field in lookup_params:
                del lookup_params[field]
        return lookup_params


class GrouperModelAdmin(ChangeListActionsMixin, ModelAdmin):
    """Easy-to-use ModelAdmin for grouper models"""

    extra_grouping_fields = ()
    change_list_template = "admin/cms/grouper/change_list.html"
    change_form_template = "admin/cms/grouper/change_form.html"

    class Media:
        js = (
            "admin/js/jquery.init.js",
            "cms/js/admin/language-selector.js",
        )

    _content_obj_cache = {}
    _content_qs_cache = {}
    _content_content_type = None
    _related_field = None

    @property
    def content_filter(self):
        return {field: getattr(self, field) for field in self.extra_grouping_fields}

    def get_language(self):
        return get_language()

    def get_language_selector(self):
        return get_language_tuple()

    def get_changelist(self, request, **kwargs):
        """Allow for extra grouping fields as a non-filter parameter"""
        return type(GrouperChangeListBase.__name__, (GrouperChangeListBase,),
                    dict(_extra_grouping_fields=self.extra_grouping_fields))

    def get_language_from_request(self, request):
        """Retrieves the language from the request"""
        return get_language_from_request(request)

    def get_grouping_from_request(self, request):
        """Retrieves the current grouping selectors from the request"""
        for field in self.extra_grouping_fields:
            if hasattr(self, f"get_{field}_from_request"):
                value = getattr(self, f"get_{field}_from_request")(request)
            else:
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__} lacks method 'get_{field}_from_request(request)' to work with "
                    f"extra_grouping_fields={self.extra_grouping_fields}"
                )
            if value != getattr(self, field, None):
                setattr(self, field, value)
                self.clear_content_cache()  # Cache belongs to different grouping

    def get_changelist_instance(self, request):
        """Set language property"""
        self.get_grouping_from_request(request)
        return super().get_changelist_instance(request)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Set grouper properties for both add and change"""
        self.get_grouping_from_request(request)
        return super().changeform_view(
            request, object_id, form_url,
            {**(extra_context or {}), **self.get_extra_context(request, object_id=object_id)},
        )

    def delete_view(self, request, object_id, extra_context=None):
        """Set grouper properties for delete"""
        self.get_grouping_from_request(request)
        return super().delete_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        """Set grouper properties for history"""
        self.get_grouping_from_request(request)
        return super().history_view(request, object_id, extra_context)

    def get_preserved_filters(self, request):
        """Always preserve grouping get parameters! Also, add them to changelist filters:
            * Save and continue will keep the grouping parameters
            * Save and returning to changelist will keep the grouping parameters
         """
        preserved_filters = dict(parse_qsl(super().get_preserved_filters(request)))
        # Extra grouping fields from property
        grouping_filters = {}
        for field in self.extra_grouping_fields:
            value = getattr(self, field, None)
            if "field" not in preserved_filters:
                grouping_filters[field] = value
        preserved_filters.update(grouping_filters)
        if "_changelist_filters" not in preserved_filters:
            preserved_filters["_changelist_filters"] = urlencode(grouping_filters)
        return urlencode(preserved_filters)

    def get_extra_context(self, request, object_id=None):
        """Provide the language to edit"""
        if object_id:
            # Instance provided? Get corresponding postconent
            obj = get_object_or_404(self.model, pk=object_id)
            content_instance = self.get_content_obj(obj)
            title = _("%(object_name)s Properties") % dict(object_name=obj._meta.verbose_name.capitalize())
        else:
            obj = None
            content_instance = None
            title = _("Add new %(object_name)s") % dict(object_name=self.model._meta.verbose_name)

        if content_instance:
            subtitle = str(content_instance)
        else:
            subtitle = _("Add content")

        extra_context = {
            "changed_message": _("Content for the current language has been changed. Click \"Cancel\" to "
                                 "return to the form and save changes. Click \"OK\" to discard changes."),
            "title": title,
            "content_instance": content_instance,
            "subtitle": subtitle
        }

        """Provide the grouping fields to edit"""
        if "language" in self.extra_grouping_fields:
            language = self.language
            if obj:
                filled_languages = self.get_content_objects(obj).values_list("language", flat=True).distinct()
            else:
                filled_languages = []

            language_tuple = get_language_tuple()
            extra_context["language_tabs"] = language_tuple
            extra_context["language"] = language
            extra_context["filled_languages"] = filled_languages
            if content_instance is None:
                subtitle = _("Add %(language)s content") % dict(language=get_language_dict().get(self.language))
                extra_context["subtitle"] = subtitle

        # TODO: Add context for other grouping fields to be shown as a dropdown
        return extra_context

    def get_form(self, request, obj=None, **kwargs):
        """Adds the language from the request to the form class"""
        form_class = super().get_form(request, obj, **kwargs)
        form_class._admin = self

        for field in self.extra_grouping_fields:
            form_class.base_fields[field].widget = forms.HiddenInput()

        if (getattr(form_class._meta, "fields", None) or "__all__") != "__all__":
            for field in self.extra_grouping_fields:
                if field not in form_class._meta.fields:
                    raise ImproperlyConfigured(
                        f"{self.__class__.__name__} needs to include all "
                        f"extra_grouping_fields={self.extra_grouping_fields} in its admin. {field} is missing."
                    )
        return form_class

    # Admin list actions defined below:
    # * View button that takes the user to the endpoint of the content model
    # * Settings button that lets the user change the grouper AND the content model
    #   using one form
    def _get_view_action(self, obj, request):
        if self.get_content_obj(obj):
            view_url = self.view_on_site(self.get_content_obj(obj))
            return self.admin_action_button(
                url=view_url,
                icon="view",
                title=_("Preview"),
                disabled=not view_url,
                keepsideframe=False,
                name="view",
            )
        return ""

    def _get_settings_action(self, obj, request):
        edit_url = admin_reverse(f"{obj._meta.app_label}_{obj._meta.model_name}_change", args=(obj.pk,))
        edit_url += f'?{urlencode(self.content_filter)}'
        return self.admin_action_button(
            url=edit_url,
            icon="settings" if self.get_content_obj(obj) else "plus",
            title=_("Settings") if self.get_content_obj(obj) else _("Add content"),
            disabled=not edit_url,
            name="settings",
        )

    def get_actions_list(self):
        return [self._get_view_action, self._get_settings_action]

    def endpoint_url(self, admin, obj):
        if self._is_content_obj(obj):
            cls = obj.__class__
            pk = obj.pk
        else:
            content = self.get_content_obj(obj)
            cls = content.__class__
            pk = content.pk

        if GrouperModelAdmin._content_content_type is None:
            # Use class as cache
            from django.contrib.contenttypes.models import ContentType

            GrouperModelAdmin._content_content_type = ContentType.objects.get_for_model(cls).pk
        try:
            return admin_reverse(admin, args=[GrouperModelAdmin._content_content_type, pk])
        except NoReverseMatch:
            return ""

    @staticmethod
    def _is_content_obj(obj):
        """Naming convention: Model classes of content objects end with "Content" """
        return obj.__class__.__name__.endswith("Content")

    def _get_content_queryset(self, obj):
        if obj not in self._content_qs_cache:
            if not self._related_field:
                for related_object in obj._meta.related_objects:
                    if related_object.related_model.__name__ == obj.__class__.__name__ + "Content":
                        self._related_field = related_object.name
                        break
                else:
                    raise AssertionError("Related field not found")
            self._content_qs_cache[obj] = getattr(obj, self._related_field)(manager="admin_manager").latest_content()
        return self._content_qs_cache[obj]

    def clear_content_cache(self):
        """Clear cache, e.g., if extra grouping field values have changed"""
        self._content_obj_cache = {}
        self._content_qs_cache = {}

    def get_content_obj(self, obj):
        if obj is None or self._is_content_obj(obj):
            return obj
        else:
            if obj not in self._content_obj_cache:
                self._content_obj_cache[obj] = self._get_content_queryset(obj) \
                    .filter(**self.content_filter) \
                    .first()
            return self._content_obj_cache[obj]

    def get_content_objects(self, obj):
        if obj is None:
            return None
        if self._is_content_obj(obj):
            # Already content object? First get grouper and the all content objects
            return self.get_content_objects(self.get_grouper_obj(obj))
        return self._get_content_queryset(obj)

    def get_grouper_obj(self, obj):
        """Get the admin object. If obj is a content object assume that the admin object
        resides in the field named after the admin model. The admin model name must be
        the same as the content model name minus "Content" at the end."""
        if self._is_content_obj(obj):
            field_name = obj.__class__.__name__[-7:].lower()
            return getattr(obj, field_name)
        return obj

    def view_on_site(self, obj):
        # Adds the View on Site button to the admin
        content_obj = self.get_content_obj(obj)
        return get_object_preview_url(content_obj) if content_obj else None

    def get_readonly_fields(self, request, obj=None):
        """Allow access to content fields to be controlled by a method "can_change_content":
        This allows versioned content to be protected if needed"""
        # First, get read-only fields for grouper
        fields = super().get_readonly_fields(request, obj)
        content_obj = self.get_content_obj(obj)
        if hasattr(self, "can_change_content"):
            if not self.can_change_content(request, content_obj):
                # Only allow content object fields to be edited if user can change them
                fields += tuple(
                    set(self.form._content_fields).difference(
                        self.extra_grouping_fields, (self.get_grouper_field_name(),),  # <= content fields
                    )
                )
        return fields

    def save_model(self, request, obj, form, change):
        """Save/create both grouper and content object"""
        super().save_model(request, obj or form.instance, form, change)
        content_dict = {
            field: form.cleaned_data[field] for field in form._content_fields if field in form.cleaned_data
        }
        if form._content_instance is None or form._content_instance.pk is None:
            # Create new using with_user syntax - requires WithUserMixin for non-versioned content models
            content_dict[self.get_grouper_field_name()] = form.instance
            form._content_model.objects.with_user(request.user).create(**content_dict)
        else:
            # Update content instance
            for key, value in content_dict.items():
                setattr(form._content_instance, key, value)
            # Finally force grouper field to point to grouper
            setattr(form._content_instance, self.get_grouper_field_name(), obj)
            form._content_instance.save()
        self.clear_content_cache()  # Make new or changed content objects visible

    def get_grouper_field_name(self):
        """Class property or lower case model name"""
        if hasattr(self, "grouper_field_name"):
            return self.grouper_field_name
        return self.model.__name__.lower()


class _GrouperModelFormMixin:
    def __init__(self, *args, **kwargs):
        assert hasattr(self, "_admin")

        if "instance" in kwargs and kwargs["instance"]:
            # Instance provided? Initialize fields from content model
            instance = kwargs["instance"]
            self._content_instance = self._admin.get_content_obj(instance)
            if self._content_instance:
                kwargs["initial"] = {
                    **{field: getattr(self._content_instance, field)
                       for field in self._content_fields},
                    **kwargs.get("initial", {})
                }
        else:
            self._content_instance = None
        super().__init__(*args, **kwargs)

        kwargs["initial"] = {
            **self._admin.content_filter,
            **kwargs.get("initial", {}),
        }

        super().__init__(*args, **kwargs)
        self.fields[self._admin.get_grouper_field_name()].widget = forms.HiddenInput()
        self.fields[self._admin.get_grouper_field_name()].required = False  # Will be set on admin model save
        self.update_field_names(self._content_fields)

    def update_field_names(self, fields):
        """Adds a language indicator to field labels"""
        if "language" in self._admin.extra_grouping_fields:
            language_dict = get_language_dict()
            for field in fields:
                if field in self.fields:
                    self.fields[field].label += f" ({language_dict[self._admin.language]})"

    def clean(self):
        if self.cleaned_data.get("language", None) not in get_language_dict():
            raise ValidationError(
                _("Invalid language %(value)s. This form cannot be processed. Try changing languages."),
                params=dict(value=self.cleaned_data.get("language", _("<unspecified>"))),
                code="invalid-language",
            )
        return super().clean()


class GrouperModelFormMixin:

    """Actually a factory class that creates the mixin. Pass the Model or ModelForm as a
    parameter::

        class MyGrouperModelForm(GrouperModelFormMixin(ContentModel), forms.ModelForm):
            model = GrouperModel
            ...

    .. warning:

        This mixin only works when used together with :class:`~cms.admin.utils.GrouperModelAdmin`.
    """

    def __new__(cls, content_model_or_form):
        if isinstance(content_model_or_form, models.base.ModelBase):
            # If a Model is passed turn it into a ModelForm
            content_model_or_form = modelform_factory(content_model_or_form, fields="__all__")
        return forms.forms.DeclarativeFieldsMetaclass(
            _GrouperModelFormMixin.__name__,
            (_GrouperModelFormMixin,),
            {
                **content_model_or_form.base_fields,  # inherit the content model form's fields
                "_content_model": content_model_or_form._meta.model,  # remember the model
                "_content_fields": content_model_or_form.base_fields.keys(),  # and which fields are from the content form
            },
        )

# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import resolve, Resolver404, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.cache import patch_cache_control
from django.utils.translation import get_language
from django.utils.http import urlquote
from django.utils.timezone import now
from django.views.generic import View

from cms.apphook_pool import apphook_pool
from cms.appresolver import get_app_urls
from cms.cache.page import get_page_cache
from cms.page_rendering import _handle_no_page, render_page
from cms.utils import get_language_from_request, get_cms_setting, get_desired_language
from cms.utils.i18n import (get_fallback_languages, force_language, get_public_languages,
                            get_redirect_on_fallback, get_language_list,
                            is_language_prefix_patterns_used, get_language_code)
from cms.utils.page_resolver import get_page_from_request


class NothingToDo(Exception):
    pass


def details(request, slug):
    view = PageView.as_view()
    return view(request, slug)


class PageView(View):
    """
    The main view of the Django-CMS! Takes a request and a slug, renders the
    page.
    """
    def dispatch(self, request, slug):
        self.request = request
        self.slug = slug
        if self.use_cache():
            return self.page_from_cache()
        else:
            return self.page_from_database()

    def use_cache(self):
        return get_cms_setting("PAGE_CACHE") and (
            not hasattr(self.request, 'toolbar') or (
                not self.request.toolbar.edit_mode and
                not self.request.toolbar.show_toolbar and
                not self.request.user.is_authenticated()
            )
        )

    def page_from_cache(self):
        cache_content = get_page_cache(self.request)
        if cache_content is not None:
            response_timestamp = now()
            content, headers, expires_datetime = cache_content
            response = HttpResponse(content)
            response._headers = headers
            # Recalculate the max-age header for this cached response
            max_age = int(
                (expires_datetime - response_timestamp).total_seconds() + 0.5)
            patch_cache_control(response, max_age=max_age)
            return response
        else:
            return self.page_from_database()

    def page_from_database(self):
        # Get a Page model object from the self.request
        page = get_page_from_request(self.request, use_path=self.slug)
        current_language = self.get_desired_language(page)
        own_urls = self.get_own_urls()
        try:
            return self.report_page_does_not_exist(page)
        except NothingToDo:
            pass
        try:
            return self.ugly_language_redirect_code(page, current_language, own_urls)
        except NothingToDo:
            pass
        try:
            return self.redirect_to_correct_slug(page, current_language)
        except NothingToDo:
            pass
        try:
            return self.follow_apphook(page, current_language)
        except NothingToDo:
            pass
        try:
            return self.follow_page_redirect(page, current_language, own_urls)
        except NothingToDo:
            pass
        try:
            return self.redirect_to_login(page)
        except NothingToDo:
            pass
        return self.ordinary_page(page, current_language)

    def report_page_does_not_exist(self, page):
        if not page:
            return _handle_no_page(self.request, self.slug)
        else:
            raise NothingToDo

    def redirect_to_correct_slug(self, page, current_language):
        page_path = self.get_page_path(page, current_language)
        page_slug = self.get_page_slug(page, current_language)
        if self.slug and self.slug != page_slug and self.request.path[:len(page_path)] != page_path:
            # The current language does not match it's slug.
            #  Redirect to the current language.
            if hasattr(self.request, 'toolbar') and self.request.user.is_staff and self.request.toolbar.edit_mode:
                self.request.toolbar.redirect_url = page_path
            else:
                return HttpResponseRedirect(page_path)
        raise NothingToDo

    def follow_apphook(self, page, current_language):
        if apphook_pool.get_apphooks():
            # There are apphooks in the pool. Let's see if there is one for the
            # current page
            # since we always have a page at this point, applications_page_check is
            # pointless
            # page = applications_page_check(request, page, slug)
            # Check for apphooks! This time for real!
            app_urls = page.get_application_urls(current_language, False)
            skip_app = False
            if (not page.is_published(current_language) and hasattr(self.request, 'toolbar')
                    and self.request.toolbar.edit_mode):
                skip_app = True
            if app_urls and not skip_app:
                app = apphook_pool.get_apphook(app_urls)
                pattern_list = []
                if app:
                    for urlpatterns in get_app_urls(app.get_urls(page, current_language)):
                        pattern_list += urlpatterns
                    try:
                        view, args, kwargs = resolve('/', tuple(pattern_list))
                        return view(self.request, *args, **kwargs)
                    except Resolver404:
                        pass
        raise NothingToDo

    def follow_page_redirect(self, page, current_language, own_urls):
        # Check if the page has a redirect url defined for this language.
        redirect_url = page.get_redirect(language=current_language)
        if redirect_url:
            if (is_language_prefix_patterns_used() and redirect_url[0] == "/"
                    and not redirect_url.startswith('/%s/' % current_language)):
                # add language prefix to url
                redirect_url = "/%s/%s" % (current_language, redirect_url.lstrip("/"))
                # prevent redirect to self

            if hasattr(self.request, 'toolbar') and self.request.user.is_staff and self.request.toolbar.edit_mode:
                self.request.toolbar.redirect_url = redirect_url
            elif redirect_url not in own_urls:
                return HttpResponseRedirect(redirect_url)
        raise NothingToDo

    def redirect_to_login(self, page):
        # permission checks
        if page.login_required and not self.request.user.is_authenticated():
            return redirect_to_login(urlquote(self.request.get_full_path()), settings.LOGIN_URL)
        else:
            raise NothingToDo

    def ordinary_page(self, page, current_language):
        if hasattr(self.request, 'toolbar'):
            self.request.toolbar.set_object(page)
        response = render_page(self.request, page, current_language=current_language, slug=self.slug)
        return response

    def get_desired_language(self, page):
        language = get_desired_language(self.request, page)
        if not language:
            # TODO: What is the use case for this?
            # This is not present in cms.utils.get_desired_language.
            language = get_language_code(get_language())
        return language

    def get_own_urls(self):
        return [
            'http%s://%s%s' % ('s' if self.request.is_secure() else '', self.request.get_host(), self.request.path),
            '/%s' % self.request.path,
            self.request.path,
        ]

    def get_page_path(self, page, current_language):
        return page.get_absolute_url(language=current_language)

    def get_page_slug(self, page, current_language):
        return page.get_path(language=current_language) or page.get_slug(language=current_language)

    def ugly_language_redirect_code(self, page, current_language, own_urls):
        # Check that the current page is available in the desired (current) language
        available_languages = []
        # this will return all languages in draft mode, and published only in live mode
        page_languages = list(page.get_published_languages())
        if hasattr(self.request, 'user') and self.request.user.is_staff:
            user_languages = get_language_list()
        else:
            user_languages = get_public_languages()
        for frontend_lang in user_languages:
            if frontend_lang in page_languages:
                available_languages.append(frontend_lang)
        # Check that the language is in FRONTEND_LANGUAGES:
        if current_language not in user_languages:
            #are we on root?
            if not self.slug:
                #redirect to supported language
                languages = []
                for language in available_languages:
                    languages.append((language, language))
                if languages:
                    # get supported language
                    new_language = get_language_from_request(self.request)
                    if new_language in get_public_languages():
                        with force_language(new_language):
                            pages_root = reverse('pages-root')
                            if (hasattr(self.request, 'toolbar') and self.request.user.is_staff and self.request.toolbar.edit_mode):
                                self.request.toolbar.redirect_url = pages_root
                            elif pages_root not in own_urls:
                                return HttpResponseRedirect(pages_root)
                elif not hasattr(self.request, 'toolbar') or not self.request.toolbar.redirect_url:
                    _handle_no_page(self.request, self.slug)
            else:
                return _handle_no_page(self.request, self.slug)
        if current_language not in available_languages:
            # If we didn't find the required page in the requested (current)
            # language, let's try to find a fallback
            found = False
            for alt_lang in get_fallback_languages(current_language):
                if alt_lang in available_languages:
                    if get_redirect_on_fallback(current_language) or self.slug == "":
                        with force_language(alt_lang):
                            path = page.get_absolute_url(language=alt_lang, fallback=True)
                            # In the case where the page is not available in the
                        # preferred language, *redirect* to the fallback page. This
                        # is a design decision (instead of rendering in place)).
                        if (hasattr(self.request, 'toolbar') and self.request.user.is_staff
                                and self.request.toolbar.edit_mode):
                            self.request.toolbar.redirect_url = path
                        elif path not in own_urls:
                            return HttpResponseRedirect(path)
                    else:
                        found = True
            if not found and (not hasattr(self.request, 'toolbar') or not self.request.toolbar.redirect_url):
                # There is a page object we can't find a proper language to render it
                _handle_no_page(self.request, self.slug)
        raise NothingToDo

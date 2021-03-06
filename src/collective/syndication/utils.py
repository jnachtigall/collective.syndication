from zExceptions import NotFound
from Products.Five import BrowserView

from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.component import getUtility

from collective.syndication.interfaces import ISyndicationUtil
from collective.syndication.interfaces import IFeedSettings
from collective.syndication.interfaces import ISiteSyndicationSettings
from collective.syndication.interfaces import ISyndicatable

from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize


class SyndicationUtil(BrowserView):
    implements(ISyndicationUtil)

    def allowed_feed_types(self):
        settings = IFeedSettings(self.context)
        factory = getUtility(
            IVocabularyFactory,
            "collective.syndication.vocabularies.SyndicationFeedTypes")
        vocabulary = factory(self.context)
        types = []
        for typ in settings.feed_types:
            types.append(vocabulary.getTerm(typ))
        return [{'path': t.value, 'title': t.title} for t in types]

    def rss_url(self):
        settings = IFeedSettings(self.context)
        types = settings.feed_types
        url = self.context.absolute_url()
        if len(types) == 0:
            return url
        _type = types[0]
        return '%s/%s' % (url, _type)

    def context_allowed(self):
        if not ISyndicatable.providedBy(self.context):
            return False
        elif not self.site_enabled():
            return False
        return True

    def context_enabled(self, raise404=False):
        settings = IFeedSettings(self.context, None)
        if not self.context_allowed() or not settings.enabled:
            if raise404:
                raise NotFound
            else:
                return False
        else:
            return True

    def newsml_allowed(self):
        enabled_types = self.site_settings.newsml_enabled_types

        if not self.site_enabled():
            return False
        elif ISyndicatable.providedBy(self.context):
            settings = IFeedSettings(self.context, None)
            if settings.enabled:
                return True
        elif self.context.portal_type in enabled_types:
            return True
        return False

    def newsml_enabled(self, raise404=False):
        if not self.newsml_allowed():
            if raise404:
                raise NotFound
            else:
                return False
        else:
            return True

    @property
    @memoize
    def site_settings(self):
        try:
            registry = getUtility(IRegistry)
            return registry.forInterface(ISiteSyndicationSettings)
        except KeyError:
            return None

    def site_enabled(self):
        try:
            settings = self.site_settings
            return settings.allowed
        except AttributeError:
            return True

    def search_rss_enabled(self, raise404=False):
        try:
            settings = self.site_settings
            if settings.search_rss_enabled:
                return True
            elif raise404:
                raise NotFound
            else:
                return False
        except AttributeError:
            return True

    def show_author_info(self):
        try:
            settings = self.site_settings
            return settings.show_author_info
        except AttributeError:
            return True

    def max_items(self):
        try:
            settings = self.site_settings
            return settings.max_items
        except AttributeError:
            return 15

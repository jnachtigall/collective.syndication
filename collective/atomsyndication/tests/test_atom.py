
import sys
import unittest2 as unittest
import logging

from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from collective.atomsyndication import atom
from collective.atomsyndication.testing import INTEGRATION_TESTING

logging.basicConfig()
logger = logging.getLogger('collective.atomsyndication')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.debug(u'\nBegin collective.syndication LOG')

PROJECTNAME = 'collective.atomsyndication'
CONTENT_STRUCTURE = (dict(type='Topic',
                          id='news-1',
                          title=u"News Article Number One",
                          description=u"A brief description about the\
                                  artcile, explaining things\
                                  about stuff."
                                  ),
                                  
                     dict(type='Topic',
                          id='news-2',
                          title=u"News Article Number Two",
                          description=u"A brief description about the\
                                  artcile, explaining things\
                                  about stuff."),
                    )
class TestSetup(unittest.TestCase):
    """ Checks instalation of this product """

    layer = INTEGRATION_TESTING

    def populateSite(self, container):
        setRoles(container, TEST_USER_ID, ['Manager'])
        login(container, TEST_USER_NAME)
        for item in CONTENT_STRUCTURE:
            container.invokeFactory(item["type"],
                                    id=item["id"],
                                    title=item["title"],
                                    description=item["description"],
                                    )
            container[item["id"]].reindexObject()

        setRoles(container, TEST_USER_ID, ['Member'])

    def test_atom_installed(self):
        portal = self.layer['portal']
        portal_quickinstaller = portal.portal_quickinstaller
        self.failUnless(portal_quickinstaller.isProductInstalled(PROJECTNAME),
                                            '%s not installed' % PROJECTNAME)


    def test_root_atom_enabled(self):
        portal = self.layer['portal']
        #self.loginAsPortalOwner()
        self.populateSite(portal)
        req = TestRequest()
        #view = getMultiAdapter((self.portal, TestRequest()), name=u"atom.xml")
        view = atom.RootAtomFeedView(portal, None)
        #view = self.portal.restrictedTraverse("atom.xml")
        view.update()

        logger.debug(u"\nQuery: %s" % view.query)
        logger.debug(u"\nCatalog search: %s" % view.query_catalog(view.query))
        logger.debug(u"\nResults: %s" % view.results)
        rendered = view.render()
        logger.debug(u"\nView: %s" % view.render())



def test_suite():
    suite= unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

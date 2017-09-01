# -*- coding: utf-8 -*-
"""Test add/remove scripts and page templates."""

from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContent
from collective.ambidexterity.default import addDefaultScript
from collective.ambidexterity.utilities import getAmbidexterityScript

import unittest


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.pr = self.portal.portal_resources

        applyProfile(self.portal, 'collective.ambidexterity:testing')

        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        test_item.id = 'test_item'
        self.portal['test_item'] = test_item

    def test_add_default_script(self):
        addDefaultScript('simple_test_type', 'test_integer_field')
        my_script = getAmbidexterityScript('simple_test_type', 'test_integer_field', 'default.py')
        self.assertTrue('default = None' in my_script)

# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from collective.ambidexterity.tests.classtest import MethodBinder
from new import instancemethod
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContent
from zope.dottedname.resolve import resolve as dottedname_resolve
from zope.schema.interfaces import IContextAwareDefaultFactory

import unittest


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        applyProfile(self.portal, 'collective.ambidexterity:testing')

        self.my_object = dottedname_resolve('collective.ambidexterity.tests.classtest.method_binder_object')
        self.my_method = dottedname_resolve('collective.ambidexterity.tests.classtest.method_binder_object.default')
        self.my_method2 = dottedname_resolve('collective.ambidexterity.tests.classtest.method_binder_object.default2')

    def test_resolve(self):
        self.assertIsInstance(self.my_object, MethodBinder)
        self.assertIsInstance(self.my_method, instancemethod)
        self.assertTrue(IContextAwareDefaultFactory.providedBy(self.my_method))
        self.assertEqual(self.my_method(None), 42)
        self.assertEqual(self.my_method(self.portal), 42)
        self.assertEqual(self.my_method2(self.portal), u'Plone site is 42')

    def test_dict_resolve(self):
        sample_method = dottedname_resolve(
            'collective.ambidexterity.tests.classtest.test_obj.sample1.default')
        self.assertTrue(IContextAwareDefaultFactory.providedBy(sample_method))
        self.assertEqual(sample_method(None), 42)

    def test_depth_resolve(self):
        sample_method = dottedname_resolve(
            'collective.ambidexterity.tests.classtest.test_obj.node.sample2.default2')
        self.assertTrue(IContextAwareDefaultFactory.providedBy(sample_method))
        self.assertEqual(sample_method(self.portal), u'Plone site is 42')

    def test_integer_default(self):
        test_item = createContent('simple_test_type', title=u'Test Item')
        self.assertEqual(test_item.test_integer_field, 42)

    def test_string_default(self):
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        self.assertEqual(test_item.test_string_field, u'The Meaning of Life is 42')

# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity.resources import DottedPathNode
from collective.ambidexterity import resources
from collective.ambidexterity import factories
from collective.ambidexterity import Validator
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContent
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary

import unittest


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

        pr = self.portal.portal_resources

        pr.manage_addFolder('ambidexterity')
        pr.ambidexterity.manage_addFolder('simple_test_type')
        pr.ambidexterity.simple_test_type.manage_addFolder('test_integer_field')
        pr.ambidexterity.simple_test_type.manage_addFolder('test_string_field')
        pr.ambidexterity.simple_test_type.manage_addFolder('test_choice_field')

        field_folder = pr.ambidexterity.simple_test_type.test_string_field
        field_folder.manage_addProduct['PythonScripts'].manage_addPythonScript('validate')
        string_validator_script = field_folder.validate
        string_validator_script.ZBindings_edit([])
        string_validator_script.ZPythonScript_edit(
            'value, context=None',
            'if u"bad" in value.lower():\n  return u"value is bad: %s" % value'
        )

        field_folder = pr.ambidexterity.simple_test_type.test_string_field
        field_folder.manage_addProduct['PythonScripts'].manage_addPythonScript('default')
        string_default_script = field_folder.default
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        string_default_script.ZBindings_edit([])
        string_default_script.ZPythonScript_edit('context', 'return u"default script %s" % context.title')

        field_folder = pr.ambidexterity.simple_test_type.test_integer_field
        field_folder.manage_addProduct['PythonScripts'].manage_addPythonScript('default')
        integer_default_script = field_folder.default
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        integer_default_script.ZBindings_edit([])
        integer_default_script.ZPythonScript_edit('context', 'return 42')

        field_folder = pr.ambidexterity.simple_test_type.test_choice_field
        field_folder.manage_addProduct['PythonScripts'].manage_addPythonScript('vocabulary')
        choice_vocabulary_script = field_folder.vocabulary
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        choice_vocabulary_script.ZBindings_edit([])
        choice_vocabulary_script.ZPythonScript_edit('context', "return [(1, u'a'), (2, u'b'), (3, u'c')]")

        applyProfile(self.portal, 'collective.ambidexterity:testing')
        self.test_schema = self.portal.portal_types.simple_test_type.lookupSchema()

    def test_validator(self):
        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        field = schema.get('test_string_field')
        validator = Validator(None, None, None, field, None)
        validator.validate(u'good input')
        with self.assertRaisesRegexp(Invalid, 'value is bad: bad input'):
            validator.validate(u'bad input')

    def test_integer_default(self):
        test_item = createContent('simple_test_type', title=u'Test Item')
        self.assertEqual(test_item.test_integer_field, 42)

    def test_string_default(self):
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        self.assertEqual(test_item.test_string_field, u'default script The Meaning of Life')

    def test_vocabulary(self):

        def callWithFieldAsSelf(field, context):
            self = field
            return self.source(context)

        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        # make field an attribute of self so that vocabulary function can find it.
        field = schema.get('test_choice_field')
        vocab = callWithFieldAsSelf(field, None)
        self.assertEqual(type(vocab), type(SimpleVocabulary.fromItems([])))
        self.assertEqual([s.value for s in vocab], [u'a', u'b', u'c'])

"""
notes

fti = portal_types.typename
schema = fti.lookupSchema()
schema.validateInvariants(something)
field = schema.get('test_string_field')
field.validate(something)

schema.get('test_integer_field').validate('five')
WrongType: ('five', (<type 'int'>, <type 'long'>), 'test_integer_field')

schema.get('test_integer_field').validate(5)
None
"""

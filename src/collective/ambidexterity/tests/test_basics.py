# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity import Validator
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
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

        type_folder = pr.ambidexterity.simple_test_type
        type_folder.manage_addFile('view.pt')
        type_folder['view.pt'].update_data(
            'view.pt for <span tal:replace="context/id" />'
        )

        field_folder = pr.ambidexterity.simple_test_type.test_string_field
        field_folder.manage_addFile('validate.py')
        field_folder['validate.py'].update_data(
            'if u"bad" in value.lower():\n  print u"At %s, value is bad: %s" % (context.getId(), value)'
        )

        field_folder = pr.ambidexterity.simple_test_type.test_string_field
        field_folder.manage_addFile('default.py')
        field_folder['default.py'].update_data('default = u"default script %s" % context.title')

        field_folder = pr.ambidexterity.simple_test_type.test_integer_field
        field_folder.manage_addFile('default.py')
        integer_default_script = field_folder['default.py']
        integer_default_script.update_data('default = 42')

        field_folder = pr.ambidexterity.simple_test_type.test_choice_field
        field_folder.manage_addFile('vocabulary.py')
        choice_vocabulary_script = field_folder['vocabulary.py']
        choice_vocabulary_script.update_data("vocabulary = [(1, u'a'), (2, u'b'), (3, u'c')]")

        applyProfile(self.portal, 'collective.ambidexterity:testing')
        self.test_schema = self.portal.portal_types.simple_test_type.lookupSchema()

    def test_validator(self):
        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        field = schema.get('test_string_field')
        validator = Validator(self.portal, None, None, field, None)
        validator.validate(u'good input')
        with self.assertRaises(Invalid) as cm:
            validator.validate(u'bad input')
        self.assertEqual(cm.exception.message, u'At plone, value is bad: bad input')

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

    def test_view_default(self):
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        test_item.id = 'test_item'
        self.portal['test_item'] = test_item
        view = self.portal['test_item'].restrictedTraverse('@@ambidexterityview')
        self.assertEqual(view(), u'view.pt for test_item')

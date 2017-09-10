# -*- coding: utf-8 -*-
"""Test add/remove scripts and page templates."""

from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContent
from collective.ambidexterity.default_script import addDefaultScript
from collective.ambidexterity.default_script import updateDefaultScript
from collective.ambidexterity.default_script import rmDefaultScript
from collective.ambidexterity.validator_script import addValidatorScript
from collective.ambidexterity.validator_script import updateValidatorScript
from collective.ambidexterity.validator_script import rmValidatorScript
from collective.ambidexterity.vocabulary_script import addVocabularyScript
from collective.ambidexterity.vocabulary_script import updateVocabularyScript
from collective.ambidexterity.vocabulary_script import rmVocabularyScript
from collective.ambidexterity.view import addViewTemplate
from collective.ambidexterity.view import ViewPageTemplateResource
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

    def test_update_default_script(self):
        addDefaultScript('simple_test_type', 'test_integer_field')
        updateDefaultScript('simple_test_type', 'test_integer_field', 'default = 42')
        my_script = getAmbidexterityScript('simple_test_type', 'test_integer_field', 'default.py')
        self.assertTrue('default = 42' in my_script)

    def test_rm_default_script(self):
        addDefaultScript('simple_test_type', 'test_integer_field')
        rmDefaultScript('simple_test_type', 'test_integer_field')
        with self.assertRaises(KeyError):
            getAmbidexterityScript('simple_test_type', 'test_integer_field', 'default.py')

    def test_add_vocabulary_script(self):
        addVocabularyScript('simple_test_type', 'test_choice_field')
        my_script = getAmbidexterityScript('simple_test_type', 'test_choice_field', 'vocabulary.py')
        self.assertTrue('vocabulary = []' in my_script)

    def test_update_vocabulary_script(self):
        addVocabularyScript('simple_test_type', 'test_choice_field')
        updateVocabularyScript('simple_test_type', 'test_choice_field', "vocabulary = [('test', ), ]")
        my_script = getAmbidexterityScript('simple_test_type', 'test_choice_field', 'vocabulary.py')
        self.assertTrue("vocabulary = [('test', ), ]" in my_script)

    def test_rm_vocabulary_script(self):
        addVocabularyScript('simple_test_type', 'test_choice_field')
        rmVocabularyScript('simple_test_type', 'test_choice_field')
        with self.assertRaises(KeyError):
            getAmbidexterityScript('simple_test_type', 'test_choice_field', 'vocabulary.py')

    def test_add_validator_script(self):
        addValidatorScript('simple_test_type', 'test_string_field')
        my_script = getAmbidexterityScript('simple_test_type', 'test_string_field', 'validate.py')
        self.assertTrue('error_message =' in my_script)

    def test_update_validator_script(self):
        addValidatorScript('simple_test_type', 'test_string_field')
        updateValidatorScript('simple_test_type', 'test_string_field', "error_message = 'something'")
        my_script = getAmbidexterityScript('simple_test_type', 'test_string_field', 'validate.py')
        self.assertTrue("error_message = 'something'" in my_script)

    def test_rm_validator_script(self):
        addValidatorScript('simple_test_type', 'test_string_field')
        rmValidatorScript('simple_test_type', 'test_string_field')
        with self.assertRaises(KeyError):
            getAmbidexterityScript('simple_test_type', 'test_string_field', 'validate.py')

    def test_add_view_template(self):
        addViewTemplate('simple_test_type')
        vptr = ViewPageTemplateResource(
            'simple_test_type',
            template_name='view.pt'
        )
        body, content_type = vptr._read_file()
        self.assertTrue('This is the default Ambidexterity view' in body)
        self.assertEqual(content_type, 'text/html')

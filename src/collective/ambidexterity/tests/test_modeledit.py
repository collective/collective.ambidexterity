# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity import models
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone.app.testing import applyProfile

import unittest


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

        applyProfile(self.portal, 'collective.ambidexterity:testing')

    def test_getFTIs(self):
        ftis = models.getSimpleDexterityFTIs()
        self.assertEqual(len(ftis), 1)
        self.assertEqual(ftis[0].getId(), 'simple_test_type')
        ftis = models.getTypesWithModelSources()
        self.assertEqual(len(ftis), 1)
        self.assertEqual(ftis[0].getId(), 'simple_test_type')

    def test_usefulTypes(self):
        types = models.usefulTypes()
        self.assertEqual(len(types), 1)
        my_type = types[0]
        self.assertEquals(my_type['id'], 'simple_test_type')
        fields = my_type['fields']
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0]['defaultFactory'], 'collective.ambidexterity.default')
        self.assertEqual(fields[1]['validator'], 'collective.ambidexterity.validate')
        self.assertEqual(fields[2]['source'], 'collective.ambidexterity.vocabulary')
        self.assertEqual(fields[2]['vocab_type'], 'source')
        self.assertEqual(fields[2]['defaultFactory'], None)

    def test_getModel(self):
        root = models.getModelRoot('simple_test_type')
        self.assertEquals(root.tag, '{http://namespaces.plone.org/supermodel/schema}model')

    def test_getField(self):
        root = models.getModelRoot('simple_test_type')
        afield = models.getFieldElement(root, 'test_integer_field')
        self.assertEqual(afield.attrib['name'], 'test_integer_field')

    def test_removeDefault(self):
        s = models.getModelSource('simple_test_type')
        self.assertIn('<defaultFactory>collective.ambidexterity.default</defaultFactory>', s)
        models.removeDefaultFactory('simple_test_type', 'test_integer_field')
        models.removeDefaultFactory('simple_test_type', 'test_string_field')
        s = models.getModelSource('simple_test_type')
        self.assertNotIn('<defaultFactory>collective.ambidexterity.default</defaultFactory>', s)

    def test_addDefault(self):
        models.removeDefaultFactory('simple_test_type', 'test_integer_field')
        models.removeDefaultFactory('simple_test_type', 'test_string_field')
        s = models.getModelSource('simple_test_type')
        self.assertNotIn('<defaultFactory>collective.ambidexterity.default</defaultFactory>', s)
        models.setDefaultFactory('simple_test_type', 'test_integer_field')
        s = models.getModelSource('simple_test_type')
        self.assertIn('<defaultFactory>collective.ambidexterity.default</defaultFactory>', s)

    def test_removeVocabulary(self):
        s = models.getModelSource('simple_test_type')
        self.assertIn('<source>collective.ambidexterity.vocabulary</source>', s)
        models.removeVocabulary('simple_test_type', 'test_choice_field')
        s = models.getModelSource('simple_test_type')
        self.assertNotIn('<source>collective.ambidexterity.vocabulary</source>', s)
        self.assertIn('<values/>', s)

    def test_addVocabulary(self):
        models.removeVocabulary('simple_test_type', 'test_choice_field')
        s = models.getModelSource('simple_test_type')
        self.assertNotIn('<source>collective.ambidexterity.vocabulary</source>', s)
        self.assertIn('<values/>', s)
        models.setVocabulary('simple_test_type', 'test_choice_field')
        s = models.getModelSource('simple_test_type')
        self.assertIn('<source>collective.ambidexterity.vocabulary</source>', s)
        self.assertNotIn('<values/>', s)

    def test_removeValidator(self):
        s = models.getModelSource('simple_test_type')
        self.assertIn('form:validator="collective.ambidexterity.validate"', s)
        models.removeValidator('simple_test_type', 'test_string_field')
        s = models.getModelSource('simple_test_type')
        self.assertNotIn('validator="collective.ambidexterity.validate"', s)

    def test_setValidator(self):
        models.removeValidator('simple_test_type', 'test_string_field')
        s = models.getModelSource('simple_test_type')
        self.assertNotIn('form:validator="collective.ambidexterity.validate"', s)
        models.setValidator('simple_test_type', 'test_string_field')
        s = models.getModelSource('simple_test_type')
        self.assertIn('form:validator="collective.ambidexterity.validate"', s)

# -*- coding: utf-8 -*-
"""Test import/export."""

from collective.ambidexterity import default_script
from collective.ambidexterity import validator_script
from collective.ambidexterity import view
from collective.ambidexterity import vocabulary_script
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone.app.testing import applyProfile
from plone.protect import createToken
from zExceptions import Forbidden
from StringIO import StringIO

import unittest
import zipfile


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

        applyProfile(self.portal, 'collective.ambidexterity:testing')

    def test_unauthorizedExport(self):
        export_view = self.portal.unrestrictedTraverse('@@ambidexterity_export')
        with self.assertRaises(Forbidden):
            export_view()

    def test_export(self):
        view.addViewTemplate('simple_test_type')
        default_script.addDefaultScript('simple_test_type', 'test_string_field')
        default_script.addDefaultScript('simple_test_type', 'test_integer_field')
        validator_script.addValidatorScript('simple_test_type', 'test_string_field')
        vocabulary_script.addVocabularyScript('simple_test_type', 'test_choice_field')

        request = self.layer['request']
        form = request.form
        form['_authenticator'] = createToken()
        form['ctype'] = 'simple_test_type'

        export_view = self.portal.unrestrictedTraverse('@@ambidexterity_export')
        rez = export_view()

        # check headers
        headers = request.response.headers
        self.assertEqual(headers['content-type'], 'application/zip')
        self.assertTrue(
            headers['content-disposition'].startswith('attachment; filename=ambidexterity-simple_test_type-')
        )

        # check content
        self.assertTrue(zipfile.is_zipfile(StringIO(rez)))

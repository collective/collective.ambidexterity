# -*- coding: utf-8 -*-
"""Test audit/resync facilities for this package."""

from collective.ambidexterity import audit
from collective.ambidexterity import default_script
from collective.ambidexterity import models
from collective.ambidexterity import validator_script
from collective.ambidexterity import view
from collective.ambidexterity import vocabulary_script
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone.app.testing import applyProfile
from zope.event import notify
from plone.schemaeditor.utils import SchemaModifiedEvent

import pprint
import unittest

pprint = pprint.PrettyPrinter(indent=4).pprint


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

        applyProfile(self.portal, 'collective.ambidexterity:testing')
        view.addViewTemplate('simple_test_type')
        default_script.addDefaultScript('simple_test_type', 'test_string_field')
        default_script.addDefaultScript('simple_test_type', 'test_integer_field')
        validator_script.addValidatorScript('simple_test_type', 'test_string_field')
        vocabulary_script.addVocabularyScript('simple_test_type', 'test_choice_field')

    def test_auditPass(self):
        arez = audit.auditResourceModelMatch()
        self.assertTrue(audit.auditIsClean(arez))
        # Let's also check that in detail.
        for ctype_name, ctype_report in arez.items():
            self.assertEqual(ctype_report['problems'], [])
            for field_name, field_report in ctype_report['fields'].items():
                self.assertEqual(field_report, [])

    def test_auditFailFTI(self):
        # damage synchronization
        models.removeAmbidexterityView('simple_test_type')
        models.removeDefaultFactory('simple_test_type', 'test_string_field')
        models.removeValidator('simple_test_type', 'test_string_field')
        models.removeVocabulary('simple_test_type', 'test_choice_field')
        arez = audit.auditResourceModelMatch()
        self.assertFalse(audit.auditIsClean(arez))
        # and, check the details
        self.assertEqual(arez['simple_test_type']['problems'], [audit.NO_VIEW_IN_FTI])
        self.assertEqual(
            arez['simple_test_type']['fields']['test_string_field'],
            [audit.NO_DEFAULT_IN_FTI, audit.NO_VALIDATOR_IN_FTI]
        )
        self.assertEqual(arez['simple_test_type']['fields']['test_choice_field'], [audit.NO_VOCABULARY_IN_FTI])

    def test_auditFailMissingResources(self):
        # damage synchronization
        view.rmViewTemplate('simple_test_type', )
        default_script.rmDefaultScript('simple_test_type', 'test_string_field')
        validator_script.rmValidatorScript('simple_test_type', 'test_string_field')
        vocabulary_script.rmVocabularyScript('simple_test_type', 'test_choice_field')
        # and check audit results
        arez = audit.auditResourceModelMatch()
        self.assertFalse(audit.auditIsClean(arez))
        self.assertEqual(arez['simple_test_type']['problems'], [audit.VIEW_TEMPLATE_MISSING])
        self.assertEqual(
            arez['simple_test_type']['fields']['test_string_field'],
            [audit.DEFAULT_SCRIPT_MISSING, audit.VALIDATOR_SCRIPT_MISSING]
        )
        self.assertEqual(
            arez['simple_test_type']['fields']['test_choice_field'],
            [audit.VOCABULARY_SCRIPT_MISSING]
        )

    def test_readableReportClean(self):
        self.assertEqual(audit.readableAuditReport(), '')

    def test_readableReportWithResourcesMissing(self):
        # destroy synchronization.
        view.rmViewTemplate('simple_test_type', )
        default_script.rmDefaultScript('simple_test_type', 'test_string_field')
        validator_script.rmValidatorScript('simple_test_type', 'test_string_field')
        vocabulary_script.rmVocabularyScript('simple_test_type', 'test_choice_field')
        report = audit.readableAuditReport()
        # Now, we should have an example of every resource warning message.
        resource_errors = [
            audit.VIEW_TEMPLATE_MISSING,
            audit.DEFAULT_SCRIPT_MISSING,
            audit.VALIDATOR_SCRIPT_MISSING,
            audit.VOCABULARY_SCRIPT_MISSING,
        ]
        for err in resource_errors:
            self.assertIn(audit.WARNING_MESSAGES[err], report)

    def test_readableReportWithModelErrors(self):
        # destroy synchronization.
        models.removeAmbidexterityView('simple_test_type')
        models.removeDefaultFactory('simple_test_type', 'test_string_field')
        models.removeValidator('simple_test_type', 'test_string_field')
        models.removeVocabulary('simple_test_type', 'test_choice_field')
        report = audit.readableAuditReport()
        # Now, we should have an example of every FTI warning message.
        errors = [
            audit.NO_VIEW_IN_FTI,
            audit.NO_DEFAULT_IN_FTI,
            audit.NO_VALIDATOR_IN_FTI,
            audit.NO_VOCABULARY_IN_FTI,
        ]
        for err in errors:
            self.assertIn(audit.WARNING_MESSAGES[err], report)

    def test_resynchronize(self):
        # damage fti in all available ways
        models.removeAmbidexterityView('simple_test_type')
        models.removeDefaultFactory('simple_test_type', 'test_string_field')
        models.removeValidator('simple_test_type', 'test_string_field')
        models.removeVocabulary('simple_test_type', 'test_choice_field')
        audit.resynchronize_all()
        self.assertTrue(audit.auditIsClean(audit.auditResourceModelMatch()))

        # Remove all our scripts and templates
        view.rmViewTemplate('simple_test_type', )
        default_script.rmDefaultScript('simple_test_type', 'test_string_field')
        validator_script.rmValidatorScript('simple_test_type', 'test_string_field')
        vocabulary_script.rmVocabularyScript('simple_test_type', 'test_choice_field')
        audit.resynchronize_all()
        report = audit.auditResourceModelMatch()
        self.assertTrue(audit.auditIsClean(report))

    def test_schemaChangeSubscriber(self):
        # damage the FTI
        models.removeDefaultFactory('simple_test_type', 'test_string_field')
        # audit: we expect a problem
        self.assertFalse(audit.auditIsClean(audit.auditResourceModelMatch()))
        # Notify our subscriber that the schema has changed
        notify(SchemaModifiedEvent(self.portal.portal_types.simple_test_type))
        # Now, we expect a clean audit
        self.assertTrue(audit.auditIsClean(audit.auditResourceModelMatch()))

    def test_subscriberOKforNonAmbidexterityTypes(self):
        notify(SchemaModifiedEvent(self.portal.portal_types.Document))

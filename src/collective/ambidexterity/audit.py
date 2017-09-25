# -*- coding: utf-8 -*-
"""
    Test and fix the synchronization between Dexterity FTIs and Ambidexterity resources.
"""

from collective.ambidexterity import _
from utilities import logger

import models
import pprint
import utilities


NO_VIEW_IN_FTI = 1
NO_DEFAULT_IN_FTI = 2
NO_VALIDATOR_IN_FTI = 3
NO_VOCABULARY_IN_FTI = 4
VIEW_TEMPLATE_MISSING = 5
DEFAULT_SCRIPT_MISSING = 6
VALIDATOR_SCRIPT_MISSING = 7
VOCABULARY_SCRIPT_MISSING = 8

WARNING_MESSAGES = {
    NO_VIEW_IN_FTI: _(u"View template found, but not referenced in FTI."),
    NO_DEFAULT_IN_FTI: _(u"Default script found, but not referenced in FTI."),
    NO_VALIDATOR_IN_FTI: _(u"Validator script found, but not referenced in FTI."),
    NO_VOCABULARY_IN_FTI: _(u"Vocabulary script found, but not referenced in FTI."),
    VIEW_TEMPLATE_MISSING: _(u"FTI uses ambidexterity view, but template is missing."),
    DEFAULT_SCRIPT_MISSING: _(u"FTI source model uses ambidexterity default, but script is missing."),
    VALIDATOR_SCRIPT_MISSING: _(u"FTI source model uses ambidexterity validator, but script is missing."),
    VOCABULARY_SCRIPT_MISSING: _(u"FTI source model uses ambidexterity vocabulary, but script is missing."),
}

pprint = pprint.PrettyPrinter(indent=4).pprint


def auditResourceModelMatch():
    resources = utilities.getResourcesInventory()
    fti_support = models.typeInventory()
    rez = {}

    # run through the resource to see if they are used in the FTIs
    for ctype_name, ctype_resources in resources.items():
        irez = dict(problems=[], fields={})
        rez[ctype_name] = irez
        ctype_fti = fti_support[ctype_name]
        if ctype_resources['has_view'] and ctype_fti['view'] != '@@ambidexterityview':
            irez['problems'].append(NO_VIEW_IN_FTI)
        for field_name, field_resources in ctype_resources['fields'].items():
            field_fti = ctype_fti['fields'][field_name]
            frez = []
            irez['fields'][field_name] = frez
            if field_resources['has_default'] and field_fti['defaultFactory'] != 'collective.ambidexterity.default':
                frez.append(NO_DEFAULT_IN_FTI)
            if field_resources['has_validator'] and field_fti['validator'] != 'collective.ambidexterity.validate':
                frez.append(NO_VALIDATOR_IN_FTI)
            if field_resources['has_vocabulary'] and field_fti['source'] != 'collective.ambidexterity.vocabulary':
                frez.append(NO_VOCABULARY_IN_FTI)

        # run through the FTIs to see if there are matching resources
        for ctype_name, ctype_fti in fti_support.items():
            irez = rez.setdefault(ctype_name, dict(problems=[], fields={}))
            if ctype_fti['view'] == '@@ambidexterityview' and not resources[ctype_name]['has_view']:
                irez['problems'].append(VIEW_TEMPLATE_MISSING)
            for field_name, element in fti_support[ctype_name]['fields'].items():
                field_resources = resources[ctype_name]['fields'][field_name]
                frez = irez['fields'].setdefault(field_name, [])
                if element['defaultFactory'] == 'collective.ambidexterity.default' \
                   and not field_resources['has_default']:
                    frez.append(DEFAULT_SCRIPT_MISSING)
                if element['validator'] == 'collective.ambidexterity.validate' \
                   and not field_resources['has_validator']:
                    frez.append(VALIDATOR_SCRIPT_MISSING)
                if element['source'] == 'collective.ambidexterity.vocabulary' \
                   and not field_resources['has_vocabulary']:
                    frez.append(VOCABULARY_SCRIPT_MISSING)
    return rez


def auditIsClean(audit_rez):
    for ctype_name, ctype_report in audit_rez.items():
        if ctype_report['problems']:
            return False
        for field_name, field_report in ctype_report['fields'].items():
            if field_report:
                return False
    return True


def readableAuditReport():
    arez = auditResourceModelMatch()
    results = []
    for ctype_name, ctype_report in arez.items():
        if ctype_report['problems']:
            results += [
                "{0}: {1}".format(ctype_name, WARNING_MESSAGES[err])
                for err in ctype_report['problems']
            ]
        for field_name, field_report in ctype_report['fields'].items():
            if field_report:
                results += [
                    "{0}/{1}: {2}".format(ctype_name, field_name, WARNING_MESSAGES[err])
                    for err in field_report
                ]
    return "\n".join(results)


def resynchronize_content_type(ctype_name, ctype_report=None):
    # our strategy is to fix the FTI.
    # we won't add templates/scripts.

    if ctype_report is None:
        arez = auditResourceModelMatch()
        ctype_report = arez[ctype_name]
    for problem in ctype_report['problems']:
        if problem == NO_VIEW_IN_FTI:
            logger.info("Fixing %s: %s", ctype_name, WARNING_MESSAGES[NO_VIEW_IN_FTI])
            models.setAmbidexterityView(ctype_name)
        elif problem == VIEW_TEMPLATE_MISSING:
            models.removeAmbidexterityView(ctype_name)
            logger.info("Fixing %s: %s.", ctype_name, WARNING_MESSAGES[VIEW_TEMPLATE_MISSING])
    for field_name, field_report in ctype_report['fields'].items():
        for problem in field_report:
            if problem == NO_DEFAULT_IN_FTI:
                logger.info("Fixing %s/%s: %s", ctype_name, field_name, WARNING_MESSAGES[NO_DEFAULT_IN_FTI])
                models.setDefaultFactory(ctype_name, field_name)
            elif problem == DEFAULT_SCRIPT_MISSING:
                logger.info("Fixing %s/%s: %s", ctype_name, field_name, WARNING_MESSAGES[DEFAULT_SCRIPT_MISSING])
                models.removeDefaultFactory(ctype_name, field_name)
            elif problem == NO_VALIDATOR_IN_FTI:
                logger.info("Fixing %s/%s: %s", ctype_name, field_name, WARNING_MESSAGES[NO_VALIDATOR_IN_FTI])
                models.setValidator(ctype_name, field_name)
            elif problem == VALIDATOR_SCRIPT_MISSING:
                logger.info("Fixing %s/%s: %s", ctype_name, field_name, WARNING_MESSAGES[VALIDATOR_SCRIPT_MISSING])
                models.removeValidator(ctype_name, field_name)
            elif problem == NO_VOCABULARY_IN_FTI:
                logger.info("Fixing %s/%s: %s", ctype_name, field_name, WARNING_MESSAGES[NO_VOCABULARY_IN_FTI])
                models.setVocabulary(ctype_name, field_name)
            elif problem == VOCABULARY_SCRIPT_MISSING:
                logger.info("Fixing %s/%s: %s", ctype_name, field_name, WARNING_MESSAGES[VOCABULARY_SCRIPT_MISSING])
                models.removeVocabulary(ctype_name, field_name)


def resynchronize_all():
    arez = auditResourceModelMatch()
    for ctype_name, ctype_report in arez.items():
        resynchronize_content_type(ctype_name, ctype_report=ctype_report)

# -*- coding: utf-8 -*-
"""
    Test and fix the synchronization between Dexterity FTIs and Ambidexterity resources.
"""

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
                if element['defaultFactory'] == 'collective.ambidexterity.default' and not field_resources['has_default']:
                    frez.append(DEFAULT_SCRIPT_MISSING)
                if element['validator'] == 'collective.ambidexterity.validate' and not field_resources['has_validator']:
                    frez.append(VALIDATOR_SCRIPT_MISSING)
                if element['source'] == 'collective.ambidexterity.vocabulary' and not field_resources['has_vocabulary']:
                    frez.append(VOCABULARY_SCRIPT_MISSING)
    return rez

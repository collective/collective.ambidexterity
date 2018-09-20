# -*- coding: utf-8 -*-
"""
    Supply a Dexterity context source binder vocabulary from a Python script
    found via getAmbidexterityFile and executed via
    AmbidexterityProgram.

    The script is given one value (other than standard builtins):
    "context" -- which is either the creation folder if the item is being
    added or the item if being edited.

    The vocabulary should be assigned to "vocabulary" in the script.
    It should be a list of values or a list of items (value, title).
"""

from interpreter import AmbidexterityProgram
from utilities import addFieldScript
from utilities import getAmbidexterityFile
from utilities import getFrameLocal
from utilities import logger
from utilities import rmFieldScript
from utilities import updateFieldScript
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

import inspect
import types

VOCABULARY_SCRIPT = """# Vocabulary script.
# Use this to set the default for a Dexterity content-type field.
# This script will be executed in a RestrictedPython environment.
# Local variables available to you:
#     context -- the folder in which the item is being added.
# Set your vocabulary by assigning it to "vocabulary".
# It should be a list of values or a list of (title, value) items.

vocabulary = []
"""


@provider(IContextSourceBinder)
def vocabulary(context):
    # we expect this to be called as a method on a field.

    stack = inspect.stack()
    field = getFrameLocal(stack, 1, 'self')
    field_name = field.getName()
    ctype_name = field.interface.getName()
    logger.debug('validator called for {0}, {1}'.format(ctype_name, field_name))
    return get_vocabulary(context, ctype_name, field_name)


def get_vocabulary(context, ctype_name, field_name):
    script = getAmbidexterityFile(ctype_name, field_name, 'vocabulary.py')
    cp = AmbidexterityProgram(script)
    cp_globals = dict(context=context)
    result = cp.execute(cp_globals)['vocabulary']
    if len(result) > 0:
        if type(result[0]) not in (types.ListType, types.TupleType):
            return SimpleVocabulary.fromValues(result)
        elif len(result[0]) == 2:
            return SimpleVocabulary.fromItems(result)
        else:
            raise ValueError(
                'Vocabulary scripts must return lists of values or items.'
            )
    return SimpleVocabulary([])


def addVocabularyScript(ctype_name, field_name):
    addFieldScript(ctype_name, field_name, 'vocabulary.py', VOCABULARY_SCRIPT)


def rmVocabularyScript(ctype_name, field_name):
    rmFieldScript(ctype_name, field_name, 'vocabulary.py')


def updateVocabularyScript(ctype_name, field_name, body):
    updateFieldScript(ctype_name, field_name, 'vocabulary.py', body)

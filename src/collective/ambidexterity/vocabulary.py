# -*- coding: utf-8 -*-
"""
    Supply a Dexterity context source binder vocabulary from a Python script
    found via getAmbidexterityScript and executed via
    AmbidexterityProgram.

    The script is given one value (other than standard builtins):
    "context" -- which is either the creation folder if the item is being
    added or the item if being edited.

    The vocabulary should be assigned to "vocabulary" in the script.
    It should be a list of values or a list of items (value, title).
"""

from interpreter import AmbidexterityProgram
from utilities import getAmbidexterityScript
from utilities import getFrameLocal
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

import inspect


@provider(IContextSourceBinder)
def vocabulary(context):
    # we expect this to be called as a method on a field.

    stack = inspect.stack()
    field = getFrameLocal(stack, 1, 'self')
    field_name = field.getName()
    ctype_name = field.interface.getName()
    script = getAmbidexterityScript(ctype_name, field_name, 'vocabulary.py')
    cp = AmbidexterityProgram(script)
    cp_globals = dict(context=context)
    result = cp.execute(cp_globals)['vocabulary']
    if len(result) > 0:
        if len(result[0]) == 1:
            return SimpleVocabulary.fromValues(result)
        elif len(result[0]) == 2:
            return SimpleVocabulary.fromItems(result)
        else:
            raise ValueError(
                'Vocabulary scripts must return lists of values or items.'
            )
    return SimpleVocabulary([])

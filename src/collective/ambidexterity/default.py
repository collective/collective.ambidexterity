# -*- coding: utf-8 -*-
"""
    Supply a Dexterity context-aware default from a Python script
    found via getAmbidexterityScript and executed via
    AmbidexterityProgram.

    The script is given one value (other than standard builtins):
    "context" -- which is either the creation folder if the item is being
    added or the item if being edited.

    The vocabulary should be assigned to "default" in the script
    and should be of the type required by the field.
"""


from interpreter import AmbidexterityProgram
from utilities import getAmbidexterityScript
from utilities import getFrameLocal
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

import inspect


@provider(IContextAwareDefaultFactory)
def default(context):
    # we expect this to be called from a function that
    # has a local variable named "inst" that is the field.

    stack = inspect.stack()
    field = getFrameLocal(stack, 1, 'inst')
    field_name = field.getName()
    ctype_name = field.interface.getName()
    script = getAmbidexterityScript(ctype_name, field_name, 'default.py')
    cp = AmbidexterityProgram(script)
    return cp.execute(dict(context=context))['default']

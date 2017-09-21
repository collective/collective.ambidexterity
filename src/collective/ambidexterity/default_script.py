# -*- coding: utf-8 -*-
"""
    Supply a Dexterity context-aware default from a Python script
    found via getAmbidexterityFile and executed via
    AmbidexterityProgram.

    The script is given one value (other than standard builtins):
    "context" -- which is either the creation folder if the item is being
    added or the item if being edited.

    The vocabulary should be assigned to "default" in the script
    and should be of the type required by the field.
"""


from interpreter import AmbidexterityProgram
from Products.CMFPlone.utils import safe_unicode
from utilities import addFieldScript
from utilities import getAmbidexterityFile
from utilities import getFrameLocal
from utilities import rmFieldScript
from utilities import updateFieldScript
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

import inspect
import types

DEFAULT_SCRIPT = """# Default script.
# Use this to set the default for a Dexterity content-type field.
# This script will be executed in a RestrictedPython environment.
# Local variables available to you:
#     context -- the folder in which the item is being added.
# Set your default by assigning it to "default".
# The value you set must match the field type.

default = None
"""


@provider(IContextAwareDefaultFactory)
def default(context):
    # we expect this to be called from a function that
    # has a local variable named "inst" that is the field.

    stack = inspect.stack()
    field = getFrameLocal(stack, 1, 'inst')
    field_name = field.getName()
    ctype_name = field.interface.getName()
    if ctype_name == u'__tmp__':
        # We're inside the schema editor, adding a new field.
        return None
    script = getAmbidexterityFile(ctype_name, field_name, 'default.py')
    cp = AmbidexterityProgram(script)
    result = cp.execute(dict(context=context))['default']
    if isinstance(result, types.StringType):
        # fix a likely common error in script returns
        return safe_unicode(result)
    else:
        return result


def addDefaultScript(ctype_name, field_name):
    addFieldScript(ctype_name, field_name, 'default.py', DEFAULT_SCRIPT)


def rmDefaultScript(ctype_name, field_name):
    rmFieldScript(ctype_name, field_name, 'default.py')


def updateDefaultScript(ctype_name, field_name, body):
    updateFieldScript(ctype_name, field_name, 'default.py', body)

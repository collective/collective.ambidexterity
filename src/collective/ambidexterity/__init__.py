# -*- coding: utf-8 -*-
""" Make it possible to call Dexterity validator, vocabulary,
    and default functions as Python Scripts kept in
    portal_resources/ambidexterity/content_type_name/field_name/(default|vocabulary|validate).

    These routines determine the content type and name by inspecting
    the calling context. That information is used to find the path
    to the portal resources script.

    Example:

    If we have a Python Script that returns a default at
    portal_resources/ambidexterity/my_simple_type/my_string_field/default,
    then we may specify the field default in the Dexterity model with the
    dotted path "collective.ambidexterity.default".
"""

from plone import api
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.i18nmessageid import MessageFactory
from zope.interface import Invalid
from zope.interface import provider
from z3c.form.validator import SimpleFieldValidator
from zope.untrustedpython.interpreter import CompiledProgram
import StringIO

import inspect
import re

_ = MessageFactory('collective.ambidexterity')

plone_munge = re.compile(r"""plone_\d+_""", flags=re.IGNORECASE)


def demunge(s):
    return plone_munge.sub('', s)


def getFrameLocal(stack, level, name):
    return stack[level][0].f_locals[name]


def getAmbidexterityScript(ctype_name, field_name, id):
    pr = api.portal.get_tool(name='portal_resources')
    path = '/'.join(('ambidexterity', demunge(ctype_name), field_name, id))
    # TODO: give a meaningful message if we can't find the script
    return pr.restrictedTraverse(path).data


@provider(IContextAwareDefaultFactory)
def default(context):
    # we expect this to be called from a function that
    # has a local variable named "inst" that is the field.

    stack = inspect.stack()
    field = getFrameLocal(stack, 1, 'inst')
    field_name = field.getName()
    ctype_name = field.interface.getName()
    script = getAmbidexterityScript(ctype_name, field_name, 'default.py')
    cp = CompiledProgram(script)
    cp_globals = dict(context=context)
    cp.exec_(cp_globals)
    return cp_globals['default']


@provider(IContextSourceBinder)
def vocabulary(context):
    # we expect this to be called as a method on a field.

    stack = inspect.stack()
    field = getFrameLocal(stack, 1, 'self')
    field_name = field.getName()
    ctype_name = field.interface.getName()
    script = getAmbidexterityScript(ctype_name, field_name, 'vocabulary.py')
    cp = CompiledProgram(script)
    cp_globals = dict(context=context)
    cp.exec_(cp_globals)
    result = cp_globals['vocabulary']
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


class Validator(SimpleFieldValidator):
    def validate(self, value):
        super(Validator, self).validate(value)
        field = self.field
        field_name = field.getName()
        ctype_name = field.interface.getName()
        script = getAmbidexterityScript(ctype_name, field_name, 'validate.py')
        cp = CompiledProgram(script)
        printed = StringIO.StringIO()
        cp_globals = dict(value=value, context=self.context, untrusted_output=printed)
        cp.exec_(cp_globals)
        result = cp_globals.get('error_message')
        if result is not None:
            raise Invalid(result)
        printed.seek(0)
        result = printed.read().strip()
        if len(result) > 0:
            raise Invalid(result)

# Alias the Validator class to validate so that we can find it at
# collective.ambidexterity.validate
validate = Validator

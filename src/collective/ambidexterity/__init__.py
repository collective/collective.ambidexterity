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

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ambidexterity')


# Things we want visible at collective.ambidexterity

from default import default  # NOQA
from vocabulary import vocabulary  # NOQA
from validator import Validator  # NOQA


# Alias the Validator class to validate so that we can find it at
# collective.ambidexterity.validate
validate = Validator

# -*- coding: utf-8 -*-
"""
    Supply a z3c.form field validator from a Python script
    found via getAmbidexterityFile and executed via
    AmbidexterityProgram.

    The script is given two values (other than standard builtins):

    * "context" -- which is either the creation folder if the item is being
      added or the item if being edited.

    * "value" -- the field value submitted for validation.

    If the validator script determines the value is invalid, it should do
    one of the following:

     * print an error message using Python's "print"; or,

     * assign an error message to a variable named "error_message".

    If the value is valid, do not do either of the above.
    The absence of an error message is taken to mean all is OK.
"""

from interpreter import AmbidexterityProgram
from utilities import addFieldScript
from utilities import getAmbidexterityFile
from utilities import logger
from utilities import rmFieldScript
from utilities import updateFieldScript
from z3c.form.validator import SimpleFieldValidator
from zope.interface import Invalid


VALIDATOR_SCRIPT = """# Validator script.
# Use this to set the validator for a Dexterity content-type field.
# This script will be executed in a RestrictedPython environment.
# local variables available to you:
#     context -- the folder in which the item is being added.
#     value -- the value to test for validity.
# If the validator script determines the value is invalid, it should do
# assign an error message to a variable named "error_message".
#
# If the value is valid, do not assign a value to error_message.
# The absence of an error message is taken to mean all is OK.

# error_message = u"This is an error message."
"""


class Validator(SimpleFieldValidator):
    def validate(self, value):
        super(Validator, self).validate(value)
        field = self.field
        field_name = field.getName()
        ctype_name = field.interface.getName()
        logger.debug('validator called for {0}, {1}'.format(ctype_name, field_name))
        script = getAmbidexterityFile(ctype_name, field_name, 'validate.py')
        cp = AmbidexterityProgram(script)
        cp_globals = dict(value=value, context=self.context)
        rez = cp.execute(cp_globals)
        result = rez.get('error_message')
        if result is not None:
            raise Invalid(result)


def addValidatorScript(ctype_name, field_name):
    addFieldScript(ctype_name, field_name, 'validate.py', VALIDATOR_SCRIPT)


def rmValidatorScript(ctype_name, field_name):
    rmFieldScript(ctype_name, field_name, 'validate.py')


def updateValidatorScript(ctype_name, field_name, body):
    updateFieldScript(ctype_name, field_name, 'validate.py', body)

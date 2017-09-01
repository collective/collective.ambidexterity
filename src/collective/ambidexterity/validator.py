# -*- coding: utf-8 -*-
"""
    Supply a z3c.form field validator from a Python script
    found via getAmbidexterityScript and executed via
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
from utilities import getAmbidexterityScript
from z3c.form.validator import SimpleFieldValidator
from zope.interface import Invalid


class Validator(SimpleFieldValidator):
    def validate(self, value):
        super(Validator, self).validate(value)
        field = self.field
        field_name = field.getName()
        ctype_name = field.interface.getName()
        script = getAmbidexterityScript(ctype_name, field_name, 'validate.py')
        cp = AmbidexterityProgram(script)
        cp_globals = dict(value=value, context=self.context)
        rez = cp.execute(cp_globals)
        result = rez.get('error_message')
        if result is not None:
            raise Invalid(result)
        result = rez['_print']().strip()
        if len(result) > 0:
            raise Invalid(result)

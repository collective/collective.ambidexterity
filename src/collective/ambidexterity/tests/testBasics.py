# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContent
from plone.dexterity.utils import createContentInContainer
from z3c.form.validator import SimpleFieldValidator
from z3c.form.interfaces import IValidator
from zope.component import queryMultiAdapter
from zope.dottedname.resolve import resolve as dottedname_resolve
from zope.interface import Invalid
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

import unittest

"""
TODO
Build (and destroy) global name space as it's resolved (via dottedname_resolve)
"""

# We're going to store references to validator script callables in
# a dictionary that's indexed by the class name of the copy of
# ScriptedValidator that we're saving at a dotted address.
validator_scripts = {}
default_scripts = {}


class ScriptedValidator(SimpleFieldValidator):
    """ SimpleFieldValidator that calls a Python Script
        for simple validation.
    """

    def validate(self, value):
        super(ScriptedValidator, self).validate(value)

        result = validator_scripts[self.__class__.__name__](value)
        if getattr(result, 'lower', None) is not None:
            raise Invalid(result)


def defaultFunctionFactory(scripted_default_function):

    @provider(IContextAwareDefaultFactory)
    def default(context):
        return scripted_default_function(context)

    return default


class ScriptedDefault(object):
    """ class to contain a Dexterity field validator that calls
        a Python Script for the default.
    """

    @provider(IContextAwareDefaultFactory)
    def default(self, context):
        return default_scripts[self.__class__.__name__](context)


class SimpleClass():
    pass


test_obj = SimpleClass()
test_obj.node = SimpleClass()


class TestSetup(unittest.TestCase):
    """Prove that a test class can be resolved by dotted name and
       that we can use context source provider methods of the class."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

        self.portal.portal_resources.manage_addProduct['PythonScripts'].manage_addPythonScript('validator_script')
        script = self.portal.portal_resources.validator_script
        script.ZBindings_edit([])
        script.ZPythonScript_edit('value', 'if u"bad" in value.lower():\n  return u"value is bad: %s" % value')

        self.portal.portal_resources.manage_addProduct['PythonScripts'].manage_addPythonScript('string_default')
        script = self.portal.portal_resources.string_default
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        script.ZBindings_edit([])
        script.ZPythonScript_edit('context', 'return u"default script %s" % context.title')

        self.portal.portal_resources.manage_addProduct['PythonScripts'].manage_addPythonScript('integer_default')
        script = self.portal.portal_resources.integer_default
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        script.ZBindings_edit([])
        script.ZPythonScript_edit('context', 'return 42')

        global test_obj
        global validator_scripts
        global default_scripts

        test_obj.node.validator = type(
            'CopyOfScriptedValidator',
            (ScriptedValidator,),
            {},
        )
        validator_scripts['CopyOfScriptedValidator'] = api.portal.get_tool(name='portal_resources').validator_script

        test_obj.node.integer_default = defaultFunctionFactory(self.portal.portal_resources.integer_default)
        test_obj.node.string_default = defaultFunctionFactory(self.portal.portal_resources.string_default)

        applyProfile(self.portal, 'collective.ambidexterity:testing')
        self.test_schema = self.portal.portal_types.simple_test_type.lookupSchema()

    def test_validator_script(self):
        self.assertEqual(self.portal.portal_resources.validator_script('bad 42'), u"value is bad: bad 42")
        self.assertEqual(self.portal.portal_resources.validator_script('good 42'), None)

    def test_validator_via_item(self):
        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        field = schema.get('test_string_field')
        validator_class = test_obj.node.validator
        validator = validator_class(None, None, None, field, None)
        validator.validate(u'good input')
        with self.assertRaisesRegexp(Invalid, 'value is bad: bad input'):
            validator.validate(u'bad input')

    def test_integer_default(self):
        test_item = createContent('simple_test_type', title=u'Test Item')
        self.assertEqual(test_item.test_integer_field, 42)

    def test_string_default(self):
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        self.assertEqual(test_item.test_string_field, u'default script The Meaning of Life')

"""
notes

fti = portal_types.typename
schema = fti.lookupSchema()
schema.validateInvariants(something)
field = schema.get('test_string_field')
field.validate(something)

schema.get('test_integer_field').validate('five')
WrongType: ('five', (<type 'int'>, <type 'long'>), 'test_integer_field')

schema.get('test_integer_field').validate(5)
None
"""

# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from new import instancemethod
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


class ScriptedValidator(SimpleFieldValidator):
    """ SimpleFieldValidator that calls a Python Script
        for simple validation. """

    def validate(self, value):
        super(ScriptedValidator, self).validate(value)

        result = validator_scripts[self.__class__.__name__](value)
        if getattr(result, 'lower', None) is not None:
            raise Invalid(result)


class MethodBinder():

    @provider(IContextAwareDefaultFactory)
    def default(self, context):
        return 42

    @provider(IContextAwareDefaultFactory)
    def default2(self, context):
        return context.title + u' is 42'

    @provider(IContextAwareDefaultFactory)
    def default3(self, context):
        portal_resources = api.portal.get_tool(name='portal_resources')
        return portal_resources.test_me(context)


class SimpleClass():
    pass


method_binder_object = MethodBinder()

test_obj = SimpleClass()
test_obj.sample1 = MethodBinder()
test_obj.node = SimpleClass()
test_obj.node.sample2 = MethodBinder()


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

        global test_obj
        test_obj.node.validator = type(
            'CopyOfScriptedValidator',
            (ScriptedValidator,),
            dict(validator_script=api.portal.get_tool(name='portal_resources').validator_script),
        )

        global validator_scripts
        validator_scripts['CopyOfScriptedValidator'] = api.portal.get_tool(name='portal_resources').validator_script

        applyProfile(self.portal, 'collective.ambidexterity:testing')

        self.test_schema = self.portal.portal_types.simple_test_type.lookupSchema()

        self.portal.portal_resources.manage_addProduct['PythonScripts'].manage_addPythonScript('test_me')
        script = self.portal.portal_resources.test_me
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        script.ZBindings_edit([])
        script.ZPythonScript_edit('context', 'return u"test script %s" % context.title')

        self.my_object = dottedname_resolve('collective.ambidexterity.tests.testBasics.method_binder_object')
        self.my_method = dottedname_resolve('collective.ambidexterity.tests.testBasics.method_binder_object.default')
        self.my_method2 = dottedname_resolve('collective.ambidexterity.tests.testBasics.method_binder_object.default2')

    def test_resolve(self):
        self.assertIsInstance(self.my_object, MethodBinder)
        self.assertIsInstance(self.my_method, instancemethod)
        self.assertTrue(IContextAwareDefaultFactory.providedBy(self.my_method))
        self.assertEqual(self.my_method(None), 42)
        self.assertEqual(self.my_method(self.portal), 42)
        self.assertEqual(self.my_method2(self.portal), u'Plone site is 42')

    def test_dict_resolve(self):
        sample_method = dottedname_resolve(
            'collective.ambidexterity.tests.testBasics.test_obj.sample1.default')
        self.assertTrue(IContextAwareDefaultFactory.providedBy(sample_method))
        self.assertEqual(sample_method(None), 42)

    def test_depth_resolve(self):
        sample_method = dottedname_resolve(
            'collective.ambidexterity.tests.testBasics.test_obj.node.sample2.default2')
        self.assertTrue(IContextAwareDefaultFactory.providedBy(sample_method))
        self.assertEqual(sample_method(self.portal), u'Plone site is 42')

    def test_integer_default(self):
        test_item = createContent('simple_test_type', title=u'Test Item')
        self.assertEqual(test_item.test_integer_field, 42)

    def test_string_default(self):
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        self.assertEqual(test_item.test_string_field, u'The Meaning of Life is 42')

    def test_script(self):
        self.assertEqual(self.portal.portal_resources.test_me(self.portal), u'test script Plone site')

    def test_script_via_dots(self):
        sample_method = dottedname_resolve(
            'collective.ambidexterity.tests.testBasics.test_obj.sample1.default3')
        self.assertEqual(sample_method(self.portal), 'test script Plone site')

    def test_default_from_script(self):
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        self.assertEqual(test_item.test_string_field2, u'test script The Meaning of Life')

    def test_validator_script(self):
        self.assertEqual(self.portal.portal_resources.validator_script('bad 42'), u"value is bad: bad 42")
        self.assertEqual(self.portal.portal_resources.validator_script('good 42'), None)

    def test_validator_via_dots(self):
        validator = dottedname_resolve(
            'collective.ambidexterity.tests.testBasics.test_obj.node.validator')
        self.assertEqual(validator.validator_script('bad 42'), u'value is bad: bad 42')

    def test_validator_via_item(self):
        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        field = schema.get('test_string_field')
        ValidatorClass = test_obj.node.validator
        validator = ValidatorClass(None, None, None, field, None)
        validator.validate(u'good input')
        with self.assertRaisesRegexp(Invalid, 'value is bad: bad input'):
            validator.validate(u'bad input')



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

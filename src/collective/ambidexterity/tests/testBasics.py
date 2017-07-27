# -*- coding: utf-8 -*-
"""Idea tests for this package."""

from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContent
from z3c.form.validator import SimpleFieldValidator
from zope.interface import Invalid
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

import unittest

"""
TODO
Build (and destroy) global name space as it's resolved (via dottedname_resolve)
"""

# I probably need to store a path from my portal_resources object,
# then do a traverse to it at validate time.


class ScriptedValidator(SimpleFieldValidator):
    """ SimpleFieldValidator that calls a Python Script
        for simple validation.
    """

    def validate(self, value):
        super(ScriptedValidator, self).validate(value)

        validator_script = api.portal.get_tool(name='portal_resources').restrictedTraverse(self.validator_script_path)
        result = validator_script(value)
        if getattr(result, 'lower', None) is not None:
            raise Invalid(result)


def validatorClassFactory(dotted_path, scripted_validator_function):
    """ return a validator class whose name is a validator_scripts key.
    """

    global validator_scripts
    return type(
        dotted_path,
        (ScriptedValidator,),
        dict(validator_script_path=scripted_validator_function)
    )


def defaultFunctionFactory(scripted_default_function):

    @provider(IContextAwareDefaultFactory)
    def default(context):
        return scripted_default_function(context)

    return default


def vocabularyFunctionFactory(scripted_vocabulary_function):

    @provider(IContextSourceBinder)
    def vocabulary(context):
        result = scripted_vocabulary_function(context)
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

    return vocabulary


class DottedPathNode():
    """ A node in a dotted path that may contain
        other nodes, a default, a validator and/or a vocabulary.
    """

    def __init__(self, dotted_path):
        self.dotted_path = dotted_path

# global!
resources = DottedPathNode('')

# We're going to store references to validator script callables in
# a dictionary that's indexed by the class name of the copy of
# ScriptedValidator that we're saving at a dotted address.
validator_scripts = {}


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

        self.portal.portal_resources.manage_addProduct['PythonScripts'].manage_addPythonScript('test_vocabulary')
        script = self.portal.portal_resources.test_vocabulary
        # order important here. bindings must be cleared before we can set 'context' as a parameter.
        script.ZBindings_edit([])
        script.ZPythonScript_edit('context', "return [(1, u'a'), (2, u'b'), (3, u'c')]")

        global resources
        resources.simple_test_type = DottedPathNode('')
        resources.simple_test_type.test_integer_field = DottedPathNode('')
        resources.simple_test_type.test_string_field = DottedPathNode('')
        resources.simple_test_type.test_choice_field = DottedPathNode('')

        resources.simple_test_type.test_string_field.validator = validatorClassFactory(
            'ambidexterity.simple_test_type.test_string_field.validator',
            'validator_script',
        )
        resources.simple_test_type.test_integer_field.default = defaultFunctionFactory(
            self.portal.portal_resources.integer_default
        )
        resources.simple_test_type.test_string_field.default = defaultFunctionFactory(
            self.portal.portal_resources.string_default
        )
        resources.simple_test_type.test_choice_field.vocabulary = vocabularyFunctionFactory(
            self.portal.portal_resources.test_vocabulary
        )

        applyProfile(self.portal, 'collective.ambidexterity:testing')
        self.test_schema = self.portal.portal_types.simple_test_type.lookupSchema()

    def test_validator_script(self):
        self.assertEqual(self.portal.portal_resources.validator_script('bad 42'), u"value is bad: bad 42")
        self.assertEqual(self.portal.portal_resources.validator_script('good 42'), None)

    def test_validator_via_item(self):
        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        field = schema.get('test_string_field')
        validator_class = resources.simple_test_type.test_string_field.validator
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

    def test_vocabulary(self):
        fti = self.portal.portal_types.simple_test_type
        schema = fti.lookupSchema()
        field = schema.get('test_choice_field')
        source = field.source
        self.assertEqual(type(source(self)), type(SimpleVocabulary.fromItems([])))
        self.assertEqual([s.value for s in source(self)], [u'a', u'b', u'c'])

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

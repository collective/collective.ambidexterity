# -*- coding: utf-8 -*-
"""Test class that has a class method for a context source binder."""

from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


class MethodBinder(object):

    @provider(IContextAwareDefaultFactory)
    def default(self, context):
        return 42

    @provider(IContextAwareDefaultFactory)
    def default2(self, context):
        return context.title + ' is 42'


class SimpleClass(object):
    pass


method_binder_object = MethodBinder()

test_obj = SimpleClass()
test_obj.sample1 = MethodBinder()
test_obj.node = SimpleClass()
test_obj.node.sample2 = MethodBinder()

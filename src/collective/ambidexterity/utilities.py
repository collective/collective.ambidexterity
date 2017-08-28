# -*- coding: utf-8 -*-

from plone import api

import re

plone_munge = re.compile(r"""plone_\d+_""", flags=re.IGNORECASE)


def getFrameLocal(stack, level, name):
    # Return a particular local from a particular level
    # of a Python-inspect stack.
    return stack[level][0].f_locals[name]


def demunge(s):
    # Determine a content-type name from a plone-decorated type name.
    return plone_munge.sub('', s)


def getAmbidexterityScript(ctype_name, field_name, id):
    # Return the body of a text file in portal_resources/ambidexterity/content_type/field/id
    pr = api.portal.get_tool(name='portal_resources')
    path = '/'.join(('ambidexterity', demunge(ctype_name), field_name, id))
    # TODO: give a meaningful message if we can't find the script
    return pr.restrictedTraverse(path).data

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


# Use these only when mutating the ambidexterity resources,
# as they may create parent folders for the requested resource.

def getAmbidexterityFolder():
    pr = api.portal.get_tool(name='portal_resources')
    ambidexterity_folder = pr.get('ambidexterity')
    if ambidexterity_folder is None:
        pr.manage_addFolder('ambidexterity')
        ambidexterity_folder = pr.ambidexterity
    return ambidexterity_folder


def getContentTypeFolder(ctype_name):
    af = getAmbidexterityFolder()
    cfolder = af.get(ctype_name)
    if cfolder is None:
        af.manage_addFolder(ctype_name)
        cfolder = af[ctype_name]
    return cfolder


def getFieldFolder(ctype_name, field_name):
    cf = getContentTypeFolder(ctype_name)
    ffolder = cf.get(field_name)
    if ffolder is None:
        cf.manage_addFolder(field_name)
        ffolder = cf[field_name]
    return ffolder


def addFieldScript(ctype_name, field_name, script_id, body):
    assert(script_id.endswith('.py'))
    ff = getFieldFolder(ctype_name, field_name)
    assert(ff.get(script_id) is None)
    ff.manage_addFile(script_id)
    ff[script_id].update_data(body)

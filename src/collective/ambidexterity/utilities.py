# -*- coding: utf-8 -*-

from plone import api
from collective.ambidexterity import models

import re

D_FTI = 'Dexterity FTI'
SIMPLE_DEXTERITY_CLASSES = (
    'plone.dexterity.content.Container',
    'plone.dexterity.content.Item',
)
plone_munge = re.compile(r"""plone_\d+_""", flags=re.IGNORECASE)


def getFrameLocal(stack, level, name):
    # Return a particular local from a particular level
    # of a Python-inspect stack.
    return stack[level][0].f_locals[name]


def demunge(s):
    # Determine a content-type name from a plone-decorated type name.
    return plone_munge.sub('', s)


def getAmbidexterityFile(ctype_name, field_name, id):
    # ctype_name is from an interface, so it's been munged.
    # Return the body of a text file in portal_resources/ambidexterity/content_type/field/id
    pr = api.portal.get_tool(name='portal_resources')
    if field_name is None:
        path = '/'.join(('ambidexterity', demunge(ctype_name), id))
    else:
        path = '/'.join(('ambidexterity', demunge(ctype_name), field_name, id))
    # TODO: give a meaningful message if we can't find the script
    return pr.restrictedTraverse(path).data


def getDexterityTypes():
    pt = api.portal.get_tool(name='portal_types')
    return pt.objectValues(D_FTI)


def getSimpleDexterityFTIs():
    # return fti's for types that use a simple Dexterity class
    rez = []
    for fti in getDexterityTypes():
        if fti.klass in SIMPLE_DEXTERITY_CLASSES:
            rez.append(fti)
    return rez


def getTypesWithModelSources():
    return [fti for fti in getDexterityTypes() if getattr(fti, 'model_source', None)]


def getResourcesInventory():
    # return an inventory of current resources

    pr = api.portal.get_tool(name='portal_resources')
    ambidexterity_folder = pr.get('ambidexterity')
    resources = {}
    for fti in getSimpleDexterityFTIs():
        fid = fti.getId()
        content_type = dict(
            title=fti.title,
            fields={},
            has_model_source=getattr(fti, 'model_source', None) is not None,
            has_view=False,
        )
        if ambidexterity_folder is None:
            type_folder = None
        else:
            type_folder = ambidexterity_folder.get(fid)
        if type_folder is not None and type_folder.get('view.pt') is not None:
            content_type['has_view'] = True
        if content_type['has_model_source']:
            for field, title in models.getFieldList(fid):
                if type_folder is not None:
                    field_folder = type_folder.get(field)
                else:
                    field_folder = None
                if field_folder is None:
                    script_ids = []
                else:
                    script_ids = field_folder.objectIds()
                content_type['fields'][field] = dict(
                    title=title,
                    has_default='default.py' in script_ids,
                    has_validator='validate.py' in script_ids,
                    has_vocabulary='vocabulary.py' in script_ids,
                )
        resources[fid] = content_type
    return resources


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


def rmFieldScript(ctype_name, field_name, script_id):
    ff = getFieldFolder(ctype_name, field_name)
    del ff[script_id]


def updateFieldScript(ctype_name, field_name, script_id, body):
    ff = getFieldFolder(ctype_name, field_name)
    ff[script_id].update_data(body)

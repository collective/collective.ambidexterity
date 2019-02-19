# -*- coding: utf-8 -*-
"""
    Modify a dexterity schema on the fly from a Python script executed via
    AmbidexterityProgram.

    The script is given one value (other than standard builtins):
    "schema" -- which is the schema of the object being rendered by
    @@ambidexterityedit

    The schema should be edited using the plone.autoform setTaggedValue method.
    See https://github.com/plone/plone.autoform/blob/master/plone/autoform/autoform.rst
"""

from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

from collective.ambidexterity.interpreter import AmbidexterityProgram
from collective.ambidexterity.utilities import getContentTypeFolder
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from zope.interface.interface import InterfaceClass

ModuleSecurityInfo('plone.autoform.interfaces').setDefaultAccess('allow')
ModuleSecurityInfo('z3c.form.interfaces').setDefaultAccess('allow')
allow_class(InterfaceClass)

SCHEMA_SCRIPT = """# Schema Editor Script
# You can modify the schema to be rendered using the setTaggedValue method
# provided by plone.autoform. See
# https://github.com/plone/plone.autoform/blob/master/plone/autoform/autoform.rst

"""

class AmbidexterityEditForm(DefaultEditForm):
    """ An edit view that allows a user to modify the form before being
        rendered.
    """

    def __init__(self, *args):
        super(AmbidexterityEditForm, self).__init__(*args)

    def updateFields(self):
        """
        Overrides the dexterity updateFields, creates a copy of the schema,
        allows the schema to be updated with RestrictedPython before setting
        the schema back to how it was after the fields are updated.
        This allows plone.autoform functions to be called on the schema during
        form processing.
        :return:
        """
        otv = self.schema._Element__tagged_values
        tv = getattr(self.schema, '_Element__tagged_values')
        tv = tv and tv or {}
        self.schema._Element__tagged_values = dict(tv)
        cf = getContentTypeFolder(self.portal_type)
        script = cf.get('schema.py')
        if script is None:
            return super(AmbidexterityEditForm, self).updateFields()

        # Provide the current workflow state of the context
        state = ''
        wft = self.context.portal_workflow
        cur_wf = wft.getWorkflowsFor(self.context)
        if len(cur_wf) > 0:
            cur_wf = cur_wf[0].id
            state = wft.getStatusOf(cur_wf, self.context)['review_state']

        cp = AmbidexterityProgram(script.data)
        cp_globals = dict(schema=self.schema, context=self.context, state=state)
        try:
            cp.execute(cp_globals)
            super(AmbidexterityEditForm, self).updateFields()
        except Exception as e:
            # Exception is caught, schema reset and exception is re-raised to
            # prevent the schema from being permanently modified.
            self.schema._Element__tagged_values = otv
            super(AmbidexterityEditForm, self).updateFields()
            raise Exception(e)
        self.schema._Element__tagged_values = otv


AmbidexterityEdit = layout.wrap_form(AmbidexterityEditForm)


def addCustomSchema(ctype_name, template_id="schema.py"):
    cf = getContentTypeFolder(ctype_name)
    assert(cf.get(template_id) is None)
    cf.manage_addFile(template_id)
    cf[template_id].update_data(SCHEMA_SCRIPT)


def updateCustomSchema(ctype_name, body, template_id="schema.py"):
    cf = getContentTypeFolder(ctype_name)
    cf[template_id].update_data(body)


def rmCustomSchema(ctype_name, template_id="schema.py"):
    cf = getContentTypeFolder(ctype_name)
    del cf[template_id]

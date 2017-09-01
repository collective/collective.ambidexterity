# -*- coding: utf-8 -*-
"""
    If a view.pt template file is placed at portal_resources/ambidexterity/content_type/view.portal_type
    as a text file, it will be usable at @@ambidexterityview.

    You may also set other template files and traverse to them at URLs like @@ambidexterityview/custom_file.js.

    TODO:
        * make sure security is still working after my minor intervention
          in traversal.
"""


from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
from collective.ambidexterity.utilities import getContentTypeFolder


BASE_VIEW_TEMPLATE = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
    xmlns:tal="http://xml.zope.org/namespaces/tal"
    xmlns:metal="http://xml.zope.org/namespaces/metal"
    xmlns:i18n="http://xml.zope.org/namespaces/i18n"
    lang="en"
    metal:use-macro="context/main_template/macros/master"
    i18n:domain="plone">
<body>

<metal:content-core fill-slot="content-core">
<metal:content-core define-macro="content-core">
  <p>
    This is the default Ambidexterity view for <span tal:replace="context/portal_type" />.
  </p>
</metal:content-core>
</metal:content-core>

</body>
</html>
"""


class ViewPageTemplateResource(ViewPageTemplateFile):
    """ Fetch template from a resource rather than a file.
    """

    def __init__(self, portal_type, template_name="view.pt", _prefix=None, content_type=None):
        _prefix = self.get_path_from_prefix(_prefix)
        # ViewPageTemplateFile.__init__() does some file checking we wish to skip.
        # super(ViewPageTemplateFile, self).__init__(filename, _prefix)
        self.filename = '/'.join(('ambidexterity', portal_type, template_name))
        if content_type is not None:
            self.content_type = content_type

    def _read_file(self):
        # zope.pagetemplate.pagetemplatefile equivalent, but fetches text
        # from portal_resources.

        pr = api.portal.get_tool(name='portal_resources')
        __traceback_info__ = self.filename  # NOQA
        try:
            resource = pr.restrictedTraverse(self.filename)
        except KeyError:
            raise KeyError(u"Ambidexterity view not implemented")
        body = resource.data
        content_type = resource.content_type
        if content_type == 'text/x-unknown-content-type' and self.filename.endswith('.pt'):
            content_type = 'text/html'
        return body, content_type


class AmbidexterityView(BrowserView):
    """ A view that fetches the template for a content type
        from portal_resources/ambidexterity/content_type
    """

    def __call__(self):
        vptr = ViewPageTemplateResource(
            self.context.portal_type,
            template_name=getattr(self, 'section', 'view.pt')
        )
        bpt = BoundPageTemplate(vptr, self)
        return bpt()

    def __getitem__(self, name):
        self.section = name
        return self


def addViewTemplate(ctype_name, template_id="view.pt"):
    cf = getContentTypeFolder(ctype_name)
    assert(cf.get(template_id) is None)
    cf.manage_addFile(template_id)
    cf[template_id].update_data(BASE_VIEW_TEMPLATE)

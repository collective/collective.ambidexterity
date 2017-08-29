
from Acquisition import aq_inner
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
# from Products.Five.browser.pagetemplatefile import sniff_type
# from Products.Five.browser.pagetemplatefile import XML_PREFIX_MAX_LENGTH


class ViewPageTemplateResource(ViewPageTemplateFile):
    """ Fetch template from a resource rather than a file.
    """

    def __init__(self, portal_type, _prefix=None, content_type=None):
        _prefix = self.get_path_from_prefix(_prefix)
        # ViewPageTemplateFile.__init__() does some file checking we wish to skip.
        # super(ViewPageTemplateFile, self).__init__(filename, _prefix)
        self.filename = portal_type
        if content_type is not None:
            self.content_type = content_type

    def _read_file(self):
        pr = api.portal.get_tool(name='portal_resources')
        path = '/'.join(('ambidexterity', self.filename, 'view.pt'))
        # TODO: give a meaningful message if we can't find the script
        body = pr.restrictedTraverse(path).data
        __traceback_info__ = self.filename
        return body, 'test/html'
        # __traceback_info__ = self.filename
        # f = open(self.filename, "rb")
        # try:
        #     text = f.read(XML_PREFIX_MAX_LENGTH)
        # except:
        #     f.close()
        #     raise
        # type_ = sniff_type(text)
        # if type_ == "text/xml":
        #     text += f.read()
        # else:
        #     # For HTML, we really want the file read in text mode:
        #     f.close()
        #     f = open(self.filename)
        #     text = f.read()
        #     text, type_ = self._prepare_html(text)
        # f.close()
        # return text, type_


class AmbidexterityView(BrowserView):
    """ A view that fetches the template for a content type
        from portal_resources/ambidexterity/content_type
    """

    def __call__(self):
        vptr = ViewPageTemplateResource('simple_test_type')
        bpt = BoundPageTemplate(vptr, self)
        return bpt()

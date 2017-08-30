# -*- coding: utf-8 -*-
""" If a view.pt template file is placed at portal_resources/ambidexterity/content_type/view.portal_type
    as a text file, it will be usable at @@ambidexterityview.
"""


from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import BoundPageTemplate


class ViewPageTemplateResource(ViewPageTemplateFile):
    """ Fetch template from a resource rather than a file.
    """

    def __init__(self, portal_type, _prefix=None, content_type=None):
        _prefix = self.get_path_from_prefix(_prefix)
        # ViewPageTemplateFile.__init__() does some file checking we wish to skip.
        # super(ViewPageTemplateFile, self).__init__(filename, _prefix)
        self.filename = '/'.join(('ambidexterity', portal_type, 'view.pt'))
        if content_type is not None:
            self.content_type = content_type

    def _read_file(self):
        # zope.pagetemplate.pagetemplatefile equivalent, but fetches text
        # from portal_resources.
        # TODO: give a meaningful message if we can't find the script

        pr = api.portal.get_tool(name='portal_resources')
        __traceback_info__ = self.filename  # NOQA
        try:
            body = pr.restrictedTraverse(self.filename).data
        except KeyError:
            raise KeyError(u"Ambidexterity view not implemented")
        type_ = sniff_type(body)
        if type_ != "text/xml":
            body, type_ = self._prepare_html(body)
        return body, type_


class AmbidexterityView(BrowserView):
    """ A view that fetches the template for a content type
        from portal_resources/ambidexterity/content_type
    """

    def __call__(self):
        vptr = ViewPageTemplateResource(self.context.portal_type)
        bpt = BoundPageTemplate(vptr, self)
        return bpt()


# from zope.pagetemplate.pagetemplatefile:

XML_PREFIXES = [
    "<?xml",                      # ascii, utf-8
    "\xef\xbb\xbf<?xml",          # utf-8 w/ byte order mark
    "\0<\0?\0x\0m\0l",            # utf-16 big endian
    "<\0?\0x\0m\0l\0",            # utf-16 little endian
    "\xfe\xff\0<\0?\0x\0m\0l",    # utf-16 big endian w/ byte order mark
    "\xff\xfe<\0?\0x\0m\0l\0",    # utf-16 little endian w/ byte order mark
]

XML_PREFIX_MAX_LENGTH = max(map(len, XML_PREFIXES))


def sniff_type(text):
    """Return 'text/xml' if text appears to be XML, otherwise return None."""
    for prefix in XML_PREFIXES:
        if text.startswith(prefix):
            return "text/xml"
    return None

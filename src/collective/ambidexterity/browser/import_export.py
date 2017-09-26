# -*- coding: utf-8 -*-

from collective.ambidexterity import utilities
from plone.protect import CheckAuthenticator
from Products.Five import BrowserView

import time


class ExportView(BrowserView):
    """ Export a zip of content-type resources """

    def __call__(self):

        CheckAuthenticator(self.request)
        ctype_name = self.request.form.get('ctype')
        if ctype_name is not None:
            # return for download
            timestamp = time.gmtime()
            format_args = (ctype_name,) + timestamp[:6]
            archive_filename = ('ambidexterity-%s-%4d%02d%02d%02d%02d%02d.zip'
                                % format_args)
            response = self.request.RESPONSE
            response.setHeader('Content-type', 'application/zip')
            response.setHeader(
                'Content-disposition',
                'attachment; filename={0}'.format(archive_filename)
            )
            return utilities.contentTypeZip(ctype_name)

# -*- coding: utf-8 -*-

from collective.ambidexterity import _
from collective.ambidexterity import audit
from collective.ambidexterity import utilities
from cStringIO import StringIO
from plone.namedfile.field import NamedFile
from plone.protect import CheckAuthenticator
from plone.z3cform.layout import wrap_form
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant

import time
import z3c.form
import zipfile
import zope.schema


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


class IZipImport(Interface):
    """ Fields for a zip import form
    """

    zip_file = NamedFile(
        title=_(u'Ambidexterity archive file'),
        required=True,
    )

    @invariant
    def isGoodImportFile(data):  # NOQA
        nfile = getattr(data, 'zip_file', None)
        if nfile is None:
            # let required validator handle this
            return None
        if not zipfile.is_zipfile(StringIO(data.zip_file.data)):
            raise Invalid(
                _(u"Error: The file submitted must be a zip archive."),
            )


@implementer(IZipImport)
class ZipImport(object):
    form_fields = z3c.form.field.Fields(IZipImport)
    zip_file = zope.schema.fieldproperty.FieldProperty(
        IZipImport['zip_file']
    )

    def __init__(self, zip_file):
        self.zip_file = zip_file


class ZipImportForm(z3c.form.form.AddForm):

    label = _(u'Import Ambidexterity resources')
    description = _(
        u"You may import view and script resources by uploading a zip archive. "
        u"The zip archive should either be an Ambidexterity export archive, "
        u"or must be structured in exactly the same way."
    )
    fields = z3c.form.field.Fields(IZipImport)
    id = 'import-zip-form'

    def create(self, data):
        return ZipImport(**data)

    def add(self, zip_import):
        summary = utilities.importResourcesZip(StringIO(zip_import.zip_file.data))
        audit.resynchronize_all()
        messages = IStatusMessage(self.request)
        messages.add(_(u"Import results:\n") + summary)

    def nextURL(self):
        url = self.context.absolute_url() + '/@@ambidexterityeditor'
        return url

ZipImportFormPage = wrap_form(ZipImportForm)

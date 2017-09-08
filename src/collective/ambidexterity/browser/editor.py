# -*- coding: utf-8 -*-

from collective.ambidexterity.utilities import getResourcesInventory
from plone.protect import CheckAuthenticator
from plone.protect.utils import addTokenToUrl
from Products.Five import BrowserView

import json


class EditorView(BrowserView):
    """Editor view.
    """

    def tokenizedURL(self, url):
        return addTokenToUrl(url)

    def resource_url(self):
        url = self.context.absolute_url() + "/@@ambidexterityajax/resource_inventory"
        return addTokenToUrl(url)


class EditorAjax(BrowserView):
    """ AJAX support
    """

    def __call__(self):
        return None

    def resource_inventory(self):
        """ Return inventory in JSON
        """

        CheckAuthenticator(self.request)

        self.request.RESPONSE.setHeader(
            'Content-Type',
            'application/json'
        )
        return json.dumps(getResourcesInventory())

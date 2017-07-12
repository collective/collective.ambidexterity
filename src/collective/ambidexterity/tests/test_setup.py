# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.ambidexterity is properly installed."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.ambidexterity is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.ambidexterity'))

    def test_browserlayer(self):
        """Test that ICollectiveAmbidexterityLayer is registered."""
        from collective.ambidexterity.interfaces import (
            ICollectiveAmbidexterityLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveAmbidexterityLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.ambidexterity'])

    def test_product_uninstalled(self):
        """Test if collective.ambidexterity is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.ambidexterity'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveAmbidexterityLayer is removed."""
        from collective.ambidexterity.interfaces import \
            ICollectiveAmbidexterityLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveAmbidexterityLayer, utils.registered_layers())

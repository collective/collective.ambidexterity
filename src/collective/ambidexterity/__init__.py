# -*- coding: utf-8 -*-
"""Init and utils."""

from resources import resources

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ambidexterity')

# reference to avoid qa warning
resources

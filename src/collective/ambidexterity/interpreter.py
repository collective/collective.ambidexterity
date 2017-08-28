# -*- coding: utf-8 -*-
"""
    zope.untrustedpython support
"""

from zope.security.checker import defineChecker
from zope.security.checker import NamesChecker
from zope.security.checker import DuplicationError
from zope.untrustedpython.interpreter import CompiledProgram
from zope.security.checker import _checkers as zsc  # for debugging

import datetime
import random
import re
import time


def declareSafe(atype):
    try:
        defineChecker(
            atype,
            NamesChecker([attribute for attribute in dir(atype) if attribute[0] != '_'])
        )
    except DuplicationError:
        print atype, "was duplicated"
        pass

# For some reason, these initializations need to be done late.
# perhaps some other module is clearing them if it's initialized
# after this.
initialized = False

def init():
    global initialized
    if not initialized:
        declareSafe(datetime)
        # The items below will cause duplicate errors.
        # declareSafe(type(datetime.date(2017, 1, 1)))
        # declareSafe(type(datetime.datetime(2017, 1, 1)))

        declareSafe(random)
        declareSafe(time)

        declareSafe(re)
        declareSafe(type(re.compile('')))
        declareSafe(type(re.compile('').match('')))
        initialized = True


class AmbidexterityProgram(CompiledProgram):

    def execute(self, locals=None, output=None):
        init()
        my_globals = dict()
        if locals is None:
            locals = {}
        self.exec_(my_globals, locals=locals, output=output)
        returned = {}
        return locals

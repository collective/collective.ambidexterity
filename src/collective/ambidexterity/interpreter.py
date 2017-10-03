# -*- coding: utf-8 -*-
"""
    RestrictedPython support
"""

from AccessControl import allow_type
from AccessControl import ModuleSecurityInfo
from RestrictedPython import compile_restricted

import datetime
import re
import AccessControl.ZopeGuards as ZopeGuards

# Make useful modules visible
for name in ('datetime', 'time', 're'):
    ModuleSecurityInfo(name).setDefaultAccess('allow')
# Include their key types
allow_type(type(re.compile('')))
allow_type(type(re.match('x', 'x')))
allow_type(type(datetime.date))  # Make sure we get class methods
allow_type(type(datetime.datetime))  # class methods
allow_type(type(datetime.date(2017, 1, 1)))
allow_type(type(datetime.datetime(2017, 1, 1)))
allow_type(type(datetime.timedelta(1)))


class AmbidexterityProgram(object):
    # set up this way in case we want to do some caching at some
    # point in the future.

    def __init__(self, code):
        self.code = compile_restricted(code, "<string>", "exec")

    def execute(self, locals=None, output=None):
        my_globals = ZopeGuards.get_safe_globals()
        my_globals['_getattr_'] = ZopeGuards.guarded_getattr
        if locals is None:
            locals = {}
        exec self.code in my_globals, locals
        return locals

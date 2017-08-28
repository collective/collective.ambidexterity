# -*- coding: utf-8 -*-
"""Test Python interpreter using zope.untrustedpython."""

from collective.ambidexterity.interpreter import AmbidexterityProgram
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa
from zope.security.interfaces import ForbiddenAttribute

import unittest


class TestSetup(unittest.TestCase):
    """Prove that our interpreter works as expected."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def test_program_simple(self):
        ap = AmbidexterityProgram("x = 1")
        rez = ap.execute()
        self.assertEqual(rez['x'], 1)

    def test_builtins(self):
        # Make sure that untrustedpython is working as we
        # understand it should.
        ap = AmbidexterityProgram("x = int('5')")
        rez = ap.execute()
        self.assertEqual(rez['x'], 5)
        with self.assertRaises(SyntaxError):
            ap = AmbidexterityProgram("try:\n    pass\nexcept:\n    pass")
        ap = AmbidexterityProgram("open('something')")
        with self.assertRaises(NameError):
            ap.execute()

    def test_imports(self):
        ap = AmbidexterityProgram("import statistics")
        with self.assertRaises(ImportError):
            ap.execute()
        ap = AmbidexterityProgram("import sys; sys.modules")
        with self.assertRaises(ForbiddenAttribute):
            ap.execute()

    def test_re_availability(self):
        ap = AmbidexterityProgram("import re; s = re.compile('te').search('atest').group(0)")
        rez = ap.execute()
        self.assertEqual(rez['s'], 'te')

    def test_random_availability(self):
        ap = AmbidexterityProgram("import random; f = random.random()")
        rez = ap.execute()
        self.assertEqual(type(rez['f']), float)

    def test_time_availability(self):
        ap = AmbidexterityProgram("import time; tt = time.time()")
        rez = ap.execute()
        import time
        self.assertEqual(type(rez['tt']), float)

    # def test_datetime_availability(self):
    #     # some module is mis-initializing the security checkers for
    #     # datetime.date and datetimes.datetime.
    #     # Until that's found and fixed, this will fail.
    #     ap = AmbidexterityProgram("import datetime; dt = datetime.date(2017, 1, 1)")
    #     rez = ap.execute()
    #     self.assertEqual(rez['dt'], datetime.date(2017, 1, 1))
    #     ap = AmbidexterityProgram("import datetime; yr = datetime.date(2017, 1, 1).year")
    #     rez = ap.execute()
    #     self.assertEqual(rez['yr'], 2017)
    #     ap = AmbidexterityProgram("import datetime; yr = datetime.datetime(2017, 1, 1).year")
    #     rez = ap.execute()
    #     self.assertEqual(rez['yr'], 2017)



# -*- coding: utf-8 -*-
"""Test our RestrictedPython setup."""

from zExceptions.unauthorized import Unauthorized
from collective.ambidexterity.interpreter import AmbidexterityProgram
from collective.ambidexterity.testing import COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING  # noqa

import plone.app.testing as pat
import unittest


class TestSetup(unittest.TestCase):
    """Prove that our interpreter works as expected."""

    layer = COLLECTIVE_AMBIDEXTERITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        pat.applyProfile(self.portal, 'collective.ambidexterity:testing')

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
        # with self.assertRaises(SyntaxError):
        #     ap = AmbidexterityProgram("try:\n    pass\nexcept:\n    pass")
        ap = AmbidexterityProgram("open('something')")
        with self.assertRaises(NameError):
            ap.execute()

    def test_imports(self):
        AmbidexterityProgram("import random").execute()
        AmbidexterityProgram("import datetime").execute()
        AmbidexterityProgram("import time").execute()
        AmbidexterityProgram("import re").execute()
        ap = AmbidexterityProgram("import statistics")
        with self.assertRaises(Unauthorized):
            ap.execute()
        ap = AmbidexterityProgram("import sys; sys.modules")
        with self.assertRaises(Unauthorized):
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
        self.assertEqual(type(rez['tt']), float)

    def test_datetime_availability(self):
        import datetime
        ap = AmbidexterityProgram("import datetime; dt = datetime.date(2017, 1, 1)")
        rez = ap.execute()
        self.assertEqual(rez['dt'], datetime.date(2017, 1, 1))
        ap = AmbidexterityProgram("import datetime; yr = datetime.date(2017, 1, 1).year")
        rez = ap.execute()
        self.assertEqual(rez['yr'], 2017)
        ap = AmbidexterityProgram("import datetime; yr = datetime.datetime(2017, 1, 1).year")
        rez = ap.execute()
        self.assertEqual(rez['yr'], 2017)
        # test class methods for datetime.date and datetime.datetime
        ap = AmbidexterityProgram("import datetime; today = datetime.date.today()")
        rez = ap.execute()
        ap = AmbidexterityProgram("import datetime; now = datetime.datetime.now()")
        rez = ap.execute()
        ap = AmbidexterityProgram("import datetime; td1 = datetime.timedelta(1).total_seconds()")
        rez = ap.execute()

    def test_object_access(self):
        # Make sure that our ability to get at a private object is dependent
        # on login.

        portal = self.portal

        from plone.dexterity.utils import createContent
        test_item = createContent('simple_test_type', title=u'The Meaning of Life')
        test_item.id = 'test_item'
        self.portal['test_item'] = test_item

        ap = AmbidexterityProgram("myid = context.getId()")
        ap.execute(dict(context=portal))
        ap = AmbidexterityProgram("myitem = context.test_item")
        ap.execute(dict(context=portal))
        ap = AmbidexterityProgram("myitem = context.test_item.getId()")
        ap.execute(dict(context=portal))

        # rock our world
        pat.logout()

        # we should still be able to get at the portal object
        ap = AmbidexterityProgram("myid = context.getId()")
        ap.execute(dict(context=portal))

        # But not our test item
        ap = AmbidexterityProgram("myitem = context.test_item")
        with self.assertRaises(Unauthorized):
            ap.execute(dict(context=portal))
        ap = AmbidexterityProgram("myitem = context.test_item.getId()")
        with self.assertRaises(Unauthorized):
            ap.execute(dict(context=portal))

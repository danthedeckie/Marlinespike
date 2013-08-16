#!.virtualenv/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

import tests.units.dictmerge as DM

dictmerge = unittest.TestLoader().loadTestsFromModule(DM)

unittest.TextTestRunner(verbosity=1).run(dictmerge)

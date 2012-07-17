#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  Marlinespike static site generator
     (C) Copyright 2012 Daniel Fairhead

    This file is part of Marlinespike.

    Marlinespike is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Marlinspike is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Marlinespike.  If not, see <http://www.gnu.org/licenses/>.

    (Just in case you're worried, files/sites you create with Marlinespike
     are your property - you don't need to GPL them or worry about legal
     stuff.  You only need to think about this stuff if you plan to redistribute
     Marlinespike itself)

"""

# preamble for PATH mangling, idea copied from Twisted.
import sys,os,string
my_path = os.path.abspath(sys.argv[0])

if os.sep+'marlinespike' in my_path:
    sys.path.insert(0,os.path.normpath(os.path.join(my_path,os.pardir, os.pardir)))

#end of preamble.

import marlinespike

marlinespike.do_dir(os.getcwd(), marlinespike._DEFAULT_CONFIG)

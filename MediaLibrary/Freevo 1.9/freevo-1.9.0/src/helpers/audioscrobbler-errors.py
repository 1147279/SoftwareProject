#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Audio scrobbler Helper to dump errors
# -----------------------------------------------------------------------
# $Id: audioscrobbler-errors.py 11435 2009-04-25 13:32:25Z duncan $
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------

try:
    import os
    import config
    f = os.path.join(config.FREEVO_CACHEDIR, 'audioscrobbler.pickle')
except ImportError:
    f = '/var/cache/freevo/audioscrobbler.pickle'
import sys
import pickle


try:
    data = pickle.load(open(f))
    for i in data:
        print i
except IOError, why:
    print 'No audioscrobbler errors detected'

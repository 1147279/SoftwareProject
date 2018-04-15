#!/usr/bin/env python
  
"""Setup script for my freevo plugin."""
  
__revision__ = "$Id: setup.py,v 1.1 2004/02/25 20:05:12 dischi Exp $"
  
from freevo.util.distribution import setup
  
# now start the python magic
setup (name = "insert-name-here",
       version = '0.1',
       description = "Full name of the plugin",
       author = "your name",
       author_email = "your mail address",
       url = "maybe a homepage"
       )

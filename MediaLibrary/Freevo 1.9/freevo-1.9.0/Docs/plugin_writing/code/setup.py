#!/usr/bin/env python

"""Setup script for my freevo plugin."""


__revision__ = "$Id: setup.py 4298 2003-11-15 12:31:34Z dischi $"

from distutils.core import setup, Extension
import distutils.command.install
import freevo.util.distutils

# now start the python magic
setup (name = "nice_plugin",
       version = '0.1',
       description = "My first plugin",
       author = "me",
       author_email = "my@mail.address",
       url = "http://i-also-have-a-web.address",

       package_dir = freevo.util.distutils.package_dir,
       packages = freevo.util.distutils.packages,
       data_files = freevo.util.distutils.data_files
       )

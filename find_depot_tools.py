# Copyright (c) 2012 Marc-Antoine Ruel. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Small utility function to find depot_tools and add it to the python path.

Will throw an ImportError exception if depot_tools can't be found since it
imports breakpad.
"""

import os
import sys

_FOUND = None


def add_depot_tools_to_path():
  """Search for depot_tools and add it to sys.path."""
  global _FOUND

  if _FOUND is None:
    # First look if depot_tools is already in PYTHONPATH.
    for i in sys.path:
      if i.rstrip(os.sep).endswith('depot_tools'):
        _FOUND = i
        break

  if _FOUND is None:
    # Then look if depot_tools is in PATH, common case.
    for i in os.environ['PATH'].split(os.pathsep):
      if i.rstrip(os.sep).endswith('depot_tools'):
        sys.path.append(i.rstrip(os.sep))
        _FOUND = i
        break

  if _FOUND is None:
    # Rare case, it's not even in PATH, look upward up to root.
    root_dir = os.path.dirname(os.path.abspath(__file__))
    while root_dir:
      if os.path.isfile(os.path.join(root_dir, 'depot_tools', 'breakpad.py')):
        i = os.path.join(root_dir, 'depot_tools')
        sys.path.append(i)
        _FOUND = i
        break
      root_dir = os.path.dirname(root_dir)

  if _FOUND is None:
    print >> sys.stderr, 'Failed to find depot_tools'
  return _FOUND


add_depot_tools_to_path()

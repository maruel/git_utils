#!/usr/bin/env python
# Copyright (c) 2012 Marc-Antoine Ruel. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Enable uses of git help for scripts in this directory and make git-foo
python scripts to be correctly executed even on Windows.

Assumes all the scripts in BASE_DIR directory are written in python for
simplicity.

There is 3 possible outcome:
- A script is found in BASE_DIR\git-[argv1], then
  - If 'help' or '--help' is provided, call the script directly with --help
    instead of deferring to the real 'git'. When the real 'git' command is
    executed with 'help', it defers to 'man' to load the man page which doesn't
    exist for these scripts.
  - Otherwise, the script is called directly with sys.executable (python) so it
    works even on Windows.
- In any other case, find back the original 'git' comamnd and defer execution to
  it.

Translates any of the follow into "python BASE_DIR/git-foo --help":
  git help foo
  git --help foo
  git foo --help

In particular, by design, it does not handle:
  git foo help

Intended side-effects:
  A python script 'git-foo' will work even on Windows without doing anything
  special.

Unintended side-effects:
  - 'python git' works.
  - Using git from inside the depot_tools directory on Windows won't call the
    shim in git_utils\git.bat because depot_tools\git.bat exists. An option is
    to hack depot_tools\git.bat accordingly.
  - It breaks git_completion; if a git br alias is created to git branch,
    git_completion will handle it just fine but git-br as a python script breaks
    git_completion. TODO(maruel): Fix this, this is annoying. In the meantime, I
    recommand setting aliases instead for the most useful commands, co, ci, br,
    etc so that git_completion processes them correctly.
"""

import os
import sys

FILE_PATH = os.path.realpath(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_PATH)

VERBOSE = False


def find_git():
  """Returns the absolute path for git found in $PATH excluding ourself."""
  if sys.platform == 'win32':
    exts = os.environ['PATHEXT'].split(os.pathsep)
    ignored = os.path.join(BASE_DIR, 'git.bat').lower()
    def ignore(path):
      return path.lower() == ignored
  else:
    exts = ['']
    ignored = os.path.join(BASE_DIR, 'git')
    def ignore(path):
      return path == ignored

  for i in os.environ['PATH'].split(os.pathsep):
    for ext in exts:
      path = os.path.realpath(os.path.join(i, 'git' + ext))
      if os.access(path, os.X_OK):
        if ignore(path):
          continue
        if VERBOSE:
          print 'Found %s' % path
        return path
  print >> sys.stderr, 'git not found'
  sys.exit(127)


def exec_command(command):
  """Runs the OS-specific os.execve() where it waits for the process to
  terminate.

  Silently handle commands 'git' and 'python'. Otherwise, it must be the
  absolute path to an executable.

  This function doesn't return.
  """
  if command[0] == 'git':
    command[0] = find_git()
  elif command[0] == 'python':
    command[0] = sys.executable

  try:
    if VERBOSE:
      print 'Previous sys.argv: %s' % sys.argv
      print 'Command: %s' % command
    if sys.platform == 'win32':
      # os.execv() doesn't wait on the child process to terminate on Windows.
      # Import subprocess here to not require it to be imported on other
      # superior OSes.
      import subprocess
      sys.exit(subprocess.call(command))
    else:
      os.execv(command[0], command)
  except SystemExit:
    raise
  except OSError, e:
    print >> sys.stderr, 'Failed to run %s' % command
    sys.exit(e.errno)
  except:
    print >> sys.stderr, 'Unknown error'
    sys.exit(125)


def is_script(cmd):
  """Returns True if it is a script in BASE_DIR that is executable."""
  return os.access(os.path.join(BASE_DIR, 'git-' + cmd), os.X_OK)


def main():
  # Find back the script name, it could be git-foo.
  cmd = sys.argv[:]
  basename = os.path.basename(cmd[0])
  if basename != os.path.basename(FILE_PATH):
    print >> sys.stderr, 'The wrapper script at %s is confused' % FILE_PATH
    sys.exit(126)

  # Replaces the executable with git by default. exec_command will handle this
  # just fine.
  cmd[0] = 'git'

  if len(cmd) == 2:
    # Special case when running the script alone.
    if is_script(cmd[1]):
      if VERBOSE:
        print 'Redirecting to script git-' + cmd[1]
      cmd = ['python', os.path.join(BASE_DIR, 'git-' + cmd[1])]
  elif len(cmd) > 2:
    if cmd[1] in ('help', '--help'):
      if is_script(cmd[2]):
        # Always specify '--help' instead of 'help' so it is processed properly
        # by the script.
        if VERBOSE:
          print 'Caught "git (--)help foo"'
        cmd = [
          'python', os.path.join(BASE_DIR, 'git-' + cmd[2]), '--help'
        ] + cmd[3:]

    elif cmd[2] == '--help':
      if is_script(cmd[1]):
        if VERBOSE:
          print 'Caught "git foo help"'
        cmd = ['python', os.path.join(BASE_DIR, 'git-' + cmd[1])] + cmd[2:]
  exec_command(cmd)


if __name__ == '__main__':
  main()

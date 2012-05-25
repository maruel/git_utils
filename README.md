git_utils
=========

Collection of git scripts written in python so they run on Windows just fine. It
also adds a git wrapper script to enhance help for these scripts.


git wrapper
-----------

The git wrapper script enables:

1.  The use of the utility scripts written in python in this directory to work on
    Windows
2.  Fixes git help foo / git foo --help to pass the command to the script, but
    only for scripts in this directory.

The scripts must be written in python so they work on Windows. Use
"git foo --help" to get help on the script usage.

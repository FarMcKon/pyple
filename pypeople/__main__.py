#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

try:
    from . import cmdline
except ValueError:
    import cmdline
cmdline.main()

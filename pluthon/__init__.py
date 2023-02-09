#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

try:
    from .pluthon_ast import *
    from .pluthon_sugar import *
    from .pluthon_functional_data import *
except ImportError as e:
    logging.error(
        "Error, trying to import dependencies. Should only occur upon package installation",
        exc_info=e,
    )

VERSION = (0, 2, 10)

__version__ = ".".join([str(i) for i in VERSION])
__author__ = "nielstron"
__author_email__ = "n.muendler@web.de"
__copyright__ = "Copyright (C) 2023 nielstron"
__license__ = "MIT"
__url__ = "https://github.com/imperatorlang/pluthon"

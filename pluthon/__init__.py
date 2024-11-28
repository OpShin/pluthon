#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

try:
    from .pluthon_ast import *  # noqa: F403
    from .pluthon_sugar import *  # noqa: F403
    from .pluthon_functional_data import *  # noqa: F403
    from .tools import *  # noqa: F403
    from .compiler_config import *  # noqa: F403
except ImportError as e:
    logging.error(
        "Error, trying to import dependencies. Should only occur upon package installation",
        exc_info=e,
    )

VERSION = (1, 0, 1)

__version__ = ".".join([str(i) for i in VERSION])
__author__ = "nielstron"
__author_email__ = "n.muendler@web.de"
__copyright__ = "Copyright (C) 2023 nielstron"
__license__ = "MIT"
__url__ = "https://github.com/opshin/pluthon"

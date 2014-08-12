# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import colorama as _colorama
    from colorama import Fore, Back, Style

    _colorama.init(autoreset=True)

    Fore = Fore
    Back = Back
    Style = Style
except ImportError:
    class _BF(object):
        BLACK = ''
        BLUE = ''
        CYAN = ''
        GREEN = ''
        MAGENTA = ''
        RED = ''
        RESET = ''
        WHITE = ''
        YELLOW = ''

    class Fore(_BF):
        pass

    class Back(_BF):
        pass

    class Style(object):
        BRIGHT = ''
        DIM = ''
        NORMAL = ''
        RESET_ALL = ''

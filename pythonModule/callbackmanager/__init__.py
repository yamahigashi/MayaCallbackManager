# -*- coding: utf-8 -*-
from . import menu
from . import entry

add = entry.add
remove = entry.remove
build_menu = menu.build_menu

__all__ = [
    "add",
    "remove",

    "build_menu"
]

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
# =============================================================================
import os
import re
from textwrap import dedent

from maya import cmds
from maya import mel

try:
    from builtins import str as text
except ImportError:
    text = unicode  # NOQA

if False:
    # For type annotation
    from typing import Dict, List, Tuple, Pattern, Callable, Any, Text  # NOQA


# =============================================================================


CONFIG_MENU_ENTRY_POINT = "callback_manager_cofig_menu"


# =============================================================================
def create_menu_entry_point():
    # type: () -> None
    """Create top menu of this package on maya main menu > window > config."""

    # build maya main menu and settings/preferences first.
    cmd = '''
    buildViewMenu MayaWindow|mainWindowMenu;
    buildPreferenceMenu mainOptionsMenu;

    string $parentName = "MayaWindow|mainWindowMenu";
    string $menuItems[] = `menu -q -ia $parentName`;

    for ($i = 0; $i < size($menuItems); $i += 1) {
        string $label = `menuItem -q -label $menuItems[$i]`;
        string $match = `match "Settings" $label`;
        if (0 < size($match)){
            $parentName = $parentName + "|" + $menuItems[$i];
            break;
        }
    }

    buildSettingsMenu $parentName;
    setParent -menu $parentName;
    '''
    if cmds.menu(CONFIG_MENU_ENTRY_POINT, exists=True):
        return

    mel.eval(cmd)

    cmds.menuItem(divider=True)
    cmds.menuItem(
        CONFIG_MENU_ENTRY_POINT,
        label="Callback Manager",
        subMenu=True,
        tearOff=True,
        # command=construct_menu
    )


def reconstruct_menu():
    # type: () -> None

    if not cmds.menu(CONFIG_MENU_ENTRY_POINT, exists=True):
        return

    cmds.menu(CONFIG_MENU_ENTRY_POINT, deleteAllItems=True, edit=True)
    fill_menu()

    # TODO(implement later): add "reset to default" command here


def fill_menu():
    # type: () -> None
    """Fill menu items with CB entries registered via entry.add()."""
    from . import entry

    for k, v in entry.get_entries().items():
        menu_name = "callback_manager_{}_on".format(k)
        checked = entry.is_enable(k)
        # print("register menu as {}".format(menu_name))
        cmds.menuItem(
            menu_name,
            label="{}".format(v.get("label").replace("_", " ").title()),
            parent=CONFIG_MENU_ENTRY_POINT,
            echoCommand=True,
            annotation=safe_encode(v.get("annotation", "")),
            checkBox=checked,
            command=dedent(
                """
                    import maya.cmds as cmds
                    {menu_name}_val = 1 if cmds.menuItem("{menu_name}", q=True, checkBox=True) else 0
                    cmds.optionVar(intValue=("{key}", {menu_name}_val))
                """.format(menu_name=menu_name, key=v.get("prefkey"))
            )
        )


# ----------------------------------------------------------------------------
def safe_encode(message):
    # type: (Text) -> Text
    """Encode utf8 into cp932."""

    try:
        message = escape_special_characters(message)
        message = text(message, "utf-8")

        if "nt" in os.name:
            message = message.encode("cp932")

        return message

    except Exception:
        return message


def escape_special_characters(string):
    # type: (Text) -> Text

    string = re.sub("&(?!&)", "&&", string)

    return string


# =============================================================================

def build_menu():
    # type: () -> None

    create_menu_entry_point()
    reconstruct_menu()

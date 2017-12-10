# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
# =============================================================================
import functools
import traceback
from collections import OrderedDict

from maya import cmds

if False:
    # For type annotation
    from typing import Dict, List, Tuple, Pattern, Callable, Any, Text  # NOQA

# =============================================================================


__CALLBACK_ENTRIES__ = OrderedDict()  # type: Dict[Text, Dict[Text, Any]]
# __CALLBACK_ENTRIES__ = OrderedDict([
#     ("auto_set_project", {"prefkey": "EnableAutoSetProject", "default": 1, "annotation": "auto set project when"}),
# ])


# =============================================================================
def get_entries():
    # type: () -> Dict[Text, Dict[Text, Any]]
    global __CALLBACK_ENTRIES__
    return __CALLBACK_ENTRIES__


def get_entry(key):
    # type: (Text) -> Dict[Text, Any]
    global __CALLBACK_ENTRIES__
    return __CALLBACK_ENTRIES__.get(key)


def get_entry_for_func(func):
    # type: (Callable) -> Dict[Text, Any]
    global __CALLBACK_ENTRIES__
    return __CALLBACK_ENTRIES__.get(get_key_name(func))


def get_keys():
    # type: () -> List[Text]
    global __CALLBACK_ENTRIES__
    return list(__CALLBACK_ENTRIES__.keys())


def get_key_name(func):
    # type: (Callable) -> Text
    key = "{}_{}".format(func.__module__, func.__name__)
    key = key.replace(".", "_")
    key = key.replace("-", "_")
    return key


def add(register_func, when, cb_func, default=True, prefkey=None, label=None):
    # type: (Callable, int, Callable, bool, Text, Text) -> int
    """Add callback.

    see [OpenMaya.MSceneMessage Class Reference](http://help.autodesk.com/view/MAYAUL/2017/ENU//?guid=__py_ref_class_open_maya_1_1_m_scene_message_html)
    for more detail.

    Args:
        register_func:  may [
            addCallback
            addCheckCallback
            addCheckFileCallback
            addCheckReferenceCallback
            addConnectionFailedCallback
            addReferenceCallback
            addStringArrayCallback
        ]
        when: may [
            kAfterCreateReference = 45
            kAfterExport = 11
            kAfterFileRead = 8
            kAfterImport = 4
            ...
            <snip>
        ]
        cb_func: The callback for invoked.
        default: Default value of callback enable.
        prefkey: The key name of entry in userPrefs.
        label: The label to display in the maya menu.

    Returns:
        int: Identifier used for removing the callback.

    Example:
        >>> import maya.api.OpenMaya as om
        >>> cb_func = lambda client_data: print("callback fired")
        >>> isinstance(add(om.MSceneMessage.addCallback, om.MSceneMessage.kBeforeNew, cb_func), int)
        True

    """
    from . import menu
    global __CALLBACK_ENTRIES__

    # decorate callback function with `execute_if_option_enable`
    cb_id = register_func(when,  execute_if_option_enable(cb_func))
    keyname = get_key_name(cb_func)

    if not prefkey:
        prefkey = "CBMAN_{}".format(keyname)

    __CALLBACK_ENTRIES__[keyname] = {
        "prefkey": prefkey,
        "id": cb_id,
        "default": 1 if default else 0,
        "label": label or keyname
    }
    set_default(cb_func)

    menu.reconstruct_menu()

    return cb_id


def remove(func):
    # type: (Callable) -> None
    """Remove the callback.

    TODO(implement later)

    """
    pass


# =============================================================================
def is_enable(key):
    # type: (Text) -> bool
    global __CALLBACK_ENTRIES__

    if key not in get_keys():
        print("!!! ERROR: {} is not defined in callback __CALLBACK_ENTRIES__. !!!!".format(key))
        return False

    option_key_name = get_entry(key).get("prefkey")
    return cmds.optionVar(q=option_key_name)


def get_default(func):
    # type: (Callable) -> Tuple[Text, Text]

    key = get_entry_for_func(func).get("prefkey")
    val = get_entry_for_func(func).get("default")

    return key, val


def set_default(func):
    # type: (Callable) -> None
    # TODO: skip if environment variable "ENABLE_SET_DEFAULT_OPTION_VAR or somekinda" is not set.
    global __CALLBACK_ENTRIES__

    try:
        key, val = get_default(func)
        cmds.optionVar(intValue=(key, val))

    except AttributeError:
        print("!!!! ERROR: __CALLBACK_ENTRIES__ entry is not found for {}. !!!!".format(func.__name__))


def execute_if_option_enable(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        global __CALLBACK_ENTRIES__

        try:
            if is_enable(get_key_name(f)):
                return f(*args, **kwargs)

            else:
                try:
                    key = get_entry_for_func(f).get("prefkey")
                    print("optionVar {} is set False, {} skipped.".format(key, f.__name__))

                except AttributeError:
                    print("__CALLBACK_ENTRIES__ entry is not found for {}.".format(f.__name__))

        except Exception:
            traceback.print_exc()

    return decorated


# =============================================================================

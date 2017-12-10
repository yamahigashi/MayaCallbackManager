# -*- coding: utf-8 -*-
import maya.utils as utils
# import maya.api.OpenMaya as om


def sample(*args, **kwargs):
    print("sample fired")


def __callbackmanager_menu_callback():
    """
    Creates menu
    """
    try:
        import callbackmanager
        callbackmanager.build_menu()
        print("finish callback manager create menu callback.")
        # callbackmanager.add(om.MSceneMessage.addCheckFileCallback, om.MSceneMessage.kBeforeOpenCheck, sample)

    except Exception:
        import traceback
        traceback.print_exc()


utils.executeDeferred('__callbackmanager_menu_callback()')

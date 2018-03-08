#!/usr/bin/env python
import threading
import copy
from functools import wraps

__author__ = 'Darryl Oatridge'


def singleton(make_instance):
    """Pattern to support a threadsafe singleton.

    Usage: in your singleton override the parent __new__(cls) with the following
        @singleton
        def __new__(cls):
            return super().__new__(cls)

    """
    __lock = threading.Lock()
    __instance = None

    @wraps(make_instance)
    def __new__(cls, *args, **kwargs):
        nonlocal __instance

        if __instance is None:
            with __lock:
                if __instance is None:
                    __instance = make_instance(cls, *args, **kwargs)

        return __instance

    return __new__


def deepcopy(obj) -> object:
    """ Thread safe deep copy of an object

    :param obj: the object to deep copy
    :return:
        a deep copy of the object
    """
    lock = threading.Lock()
    with lock:
        return copy.deepcopy(obj)

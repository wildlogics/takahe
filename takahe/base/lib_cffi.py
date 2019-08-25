#!/usr/bin/python
# -*- coding: utf-8 -*-
import vulkan


class CustomPointer():

    def __init__(self, cffi_type):

        self.cffi_pointer = vulkan.ffi.new(cffi_type)

    @property
    def cffi_value(self):

        return None if self.cffi_pointer is None else self.cffi_pointer[0]

    def destroy(self):

        if self.cffi_pointer is not None:
            vulkan.ffi.release(self.cffi_pointer)
        self.cffi_pointer = None

    def __getattr__(self, item):

        value = self.cffi_pointer[0]

        if hasattr(value, item):
            return getattr(value, item)
        else:
            return super().__getattr__(value, item)

    def __getitem__(self, item):

        return self.cffi_pointer[item]

    def __del__(self):

        self.destroy()

class Dereference():

    _pointers = None

    def __init__(self):

        self._pointers = {}

    def __getattr__(self, item):

        return self._pointers[item].cffi_value

    def __setattr__(self, key, value):

        self._pointers[key] = value


class Autoderef():

    def __init__(self, host = None, prefix = 'cp_'):

        self.__host = self if host is None else host
        self.__prefix = prefix

    def alloc(self, **kwargs):

        ret = []

        for name,cffi_type in kwargs.items():

            item = f"{self.__prefix}{name}"
            cp = CustomPointer(cffi_type)
            setattr(self.__host, item, cp)
            ret.append(cp.cffi_pointer)

        if len(ret) == 1: return ret[0]
        elif len(ret) > 1: return tuple(ret)
        else: return None


    def __getattr__(self, name):

        item = f"{self.__prefix}{name}"

        if hasattr(self.__host, item):
            target = getattr(self.__host, item)
            if isinstance(target, CustomPointer):
                return target.cffi_value
            else:
                return target
        else:
            return super().__getattr__(self, name)

    def __delattr__(self, name):

        item = f"{self.__prefix}{name}"
        if hasattr(self.__host, item):
            target = getattr(self.__host, item)
            if isinstance(target, CustomPointer):
                target.destroy()
            delattr(self.__host, item)


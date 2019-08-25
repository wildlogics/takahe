#!/usr/bin/python
# -*- coding: utf-8 -*-
import ctypes
import logging

import vulkan

from takahe.base.lib_cffi import CustomPointer
from takahe.base.types import VulkanObject


class Debugger(VulkanObject):

    LAYERS = ["VK_LAYER_KHRONOS_validation"]
    prefix = "LAYER:"

    def __init__(self, logger = None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logger = logger if logger else logging.getLogger(__name__)

    def make_messenger(self):

        return vulkan.VkDebugUtilsMessengerCreateInfoEXT(
            messageSeverity = vulkan.VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT
                            | vulkan.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT
                            | vulkan.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
                            # | vulkan.VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT,
            messageType = vulkan.VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT
                        | vulkan.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT
                        | vulkan.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
            pfnUserCallback = Debugger.callback,
            pUserData = vulkan.ffi.new_handle(self)
        )

    @staticmethod
    def callback(messageSeverity, messageType, pCallbackData, pUserData):

        try:
            self = vulkan.ffi.from_handle(pUserData)
            # self = Debugger()
        except:
            self = Debugger()

        if messageSeverity == vulkan.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT: log = self.logger.error
        elif messageSeverity == vulkan.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT: log = self.logger.warning
        else: log = self.logger.info

        message = pCallbackData.pMessage
        message = vulkan.ffi.string(message)
        message = message.decode('utf-8')
        log("%s%s" % (self.prefix, message))

        return vulkan.VK_FALSE


class CasingDebugger(Debugger):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.init()

    def init(self):

        self.info = self.make_messenger()

    def destroy(self):

        pass


class LayerDebugger(Debugger):

    def __init__(self, vulkan_instance, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.vulkan_instance = vulkan_instance
        self.init()

    @property
    def vk_instance(self):

        return self.vulkan_instance.vk_instance


    def init(self):

        self.info = self.make_messenger()

        pMessenger = self.vk.alloc(debug_messenger = 'VkDebugUtilsMessengerEXT*') # Defines self.vk_debug_messenger
        self.vulkan_instance.ext.vkCreateDebugUtilsMessengerEXT(self.vk_instance, self.info, None, pMessenger)

    def destroy(self):

        self.vulkan_instance.ext.vkDestroyDebugUtilsMessengerEXT(self.vk_instance, self.vk.debug_messenger, None)
        self.vk_debug_messenger.destroy()
        delattr(self.vk, 'debug_messenger')

# def layers(self):
#
#     layers = [layer for layer in vulkan.vkEnumerateInstanceLayerProperties()]
#     names = [layer.layerName for layer in layers]
#
#     print("Vulkan Layers:")
#     for layer in layers:
#         print(" · %s" % layer.layerName)
#
#     if not all(layer in names for layer in self.LAYERS):
#         raise Exception("Unavailable layers")



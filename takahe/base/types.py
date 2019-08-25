#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from typing import Any, List

import vulkan

from takahe.base.lib_cffi import Autoderef


class Configuration():

    name = "vulkan"
    version = (1,0,0)
    width = 1200
    height = 900
    debug = False
    loglevel = logging.INFO
    extensions = [vulkan.VK_KHR_SWAPCHAIN_EXTENSION_NAME]

    def __init__(self, **kwargs):

        for param in kwargs:

            setattr(self, param, kwargs[param])

        self.loglevel = logging.INFO if self.debug else logging.WARNING
        logging.basicConfig(format='%(levelname)s:%(message)s', level=self.loglevel)

class PhysicalDevice():

    vk_device : Any
    ext : Any

class LogicalDevice():

    vk_device : Any

class VulkanInstance():

    vk_instance : Any
    ext : Any
    layers : List[str]
    surface :Any
    physical_device : PhysicalDevice

    def create_device(self, device: PhysicalDevice, surface: 'VulkanSurface', extensions) -> LogicalDevice: pass

class VulkanSurface():

    vk_surface_id : int
    instance : VulkanInstance

class VulkanFramework():

    vulkan_instance : VulkanInstance

class BaseEnvironment() :

    config : Configuration
    logger : Any
    glfw : Any
    vulkan : VulkanFramework
    debugger : Any
    init_debugger : Any

class VulkanObject:

    def __init__(self):

        self.vk = Autoderef(self, 'vk_')
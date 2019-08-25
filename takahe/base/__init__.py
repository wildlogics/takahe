#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from takahe.base.debug import CasingDebugger, LayerDebugger
from takahe.base.lib_cffi import Autoderef
from takahe.base.lib_glfw import GraphicsLibraryFramework
from takahe.base.lib_vulkan import VulkanFramework
from takahe.base.singleton import environment
from takahe.base.types import Configuration, BaseEnvironment as Interface

class BaseEnvironment(Interface):

    def __init__(self, configuration : Configuration):

        self.config = configuration
        self.logger = logging

        environment.base = self

    def init(self):

        self.glfw = GraphicsLibraryFramework(self.logger)
        self.glfw.init(self.config)

        self.vulkan = VulkanFramework(self.logger, self.glfw.extensions)

        if self.config.debug:

            self.init_debugger = CasingDebugger()
            self.vulkan.init(self.config.name + " (debug)", self.config.version, self.init_debugger)
            self.debugger = LayerDebugger(self.vulkan.vulkan_instance)

        else:

            self.vulkan.init(self.config.name, self.config.version)

        surface = self.glfw.create_surface(self.vulkan.vulkan_instance)
        self.vulkan.set_surface(surface)

    def clean(self):

        if self.config.debug:

            self.debugger.destroy()
            self.vulkan.destroy()
            self.init_debugger.destroy()

        else:

            self.vulkan.destroy()

        self.glfw.destroy()



#!/usr/bin/python
# -*- coding: utf-8 -*-
import ctypes
import logging

import glfw
import vulkan

from takahe.base.types import Configuration, VulkanInstance


class GraphicsLibraryFramework():

    def __init__(self, logger = None):

        self.logger = logger if logger else logging.getLogger(__name__)

    def init(self, config : Configuration):

        self.glfw = glfw.init()
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        self.window = glfw.create_window(config.width, config.height, config.name, None, None)

        self.extensions = glfw.get_required_instance_extensions()

        self.logger.info("GLFW Required Extensions:")
        for extension in self.extensions:
            self.logger.info(" · %s" % extension)

    def create_surface(self, vulkan_instance : VulkanInstance):

        instance = vulkan_instance.vk_instance
        ref = int(vulkan.ffi.cast('intptr_t', instance))
        instance = ctypes.c_void_p(ref)

        opaque = vulkan.ffi.new("int *")
        pSurface = vulkan.ffi.cast('VkSurfaceKHR', opaque)

        ref = int(vulkan.ffi.cast('intptr_t', pSurface))
        glfw_surface = ctypes.c_void_p(ref)

        code = glfw.create_window_surface(instance, self.window, None, glfw_surface)

        if code != vulkan.VK_SUCCESS:

            raise RuntimeError("Unable to create window surface")

        return VulkanSurface(vulkan_instance, opaque, pSurface)

    def poll(self):

        while not glfw.window_should_close(self.window):

            glfw.poll_events()

    def destroy(self):

        glfw.destroy_window(self.window)
        glfw.terminate()


class VulkanSurface():

    def __init__(self, instance : VulkanInstance, surface_id, vk_surface):

        self.instance = instance
        self.opaque = surface_id
        self.vk_surface_id = surface_id[0]
        self.vk_surface = vk_surface

    def destroy(self):

        self.instance.ext.vkDestroySurfaceKHR(self.instance.vk_instance, self.vk_surface_id, None)
        vulkan.ffi.release(self.opaque)
